from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.models.partner import Partner
from app.models.resort import Resort
from app.models.room_type import RoomType
from app.models.room_images import RoomImage
from app.models.offer import Offer
from app.models.service import Service
from app.db_async import get_db
from app.dependencies.auth import get_current_partner
from app.schemas.room_type import (
    RoomTypeCreate, RoomTypeUpdate, RoomTypeOut, RoomImageOut,
    OfferCreate, OfferUpdate, OfferOut, OfferWithDetails, ServiceOut
)

router = APIRouter(prefix="/api/v1/partner", tags=["Partner - Room Management"])


async def verify_resort_ownership(db: AsyncSession, partner_id: int, resort_id: int) -> Resort:
    result = await db.execute(
        select(Resort).where(Resort.id == resort_id, Resort.partner_id == partner_id)
    )
    resort = result.scalars().first()
    if not resort:
        raise HTTPException(status_code=404, detail="Resort không tồn tại hoặc không thuộc quyền quản lý của bạn")
    return resort


async def verify_room_type_ownership(db: AsyncSession, partner_id: int, room_type_id: int) -> RoomType:
    result = await db.execute(
        select(RoomType)
        .join(Resort, Resort.id == RoomType.resort_id)
        .where(RoomType.id == room_type_id, Resort.partner_id == partner_id)
        .options(selectinload(RoomType.images), selectinload(RoomType.offers))
    )
    room_type = result.scalars().first()
    if not room_type:
        raise HTTPException(status_code=404, detail="Loại phòng không tồn tại hoặc không thuộc quyền quản lý của bạn")
    return room_type


# ============ Resort & Service ============

@router.get("/resorts")
async def get_my_resorts(
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Resort).where(Resort.partner_id == partner.id))
    resorts = result.scalars().all()
    return [{"id": r.id, "name": r.name, "address": r.address} for r in resorts]


@router.get("/resorts/{resort_id}/services", response_model=List[ServiceOut])
async def get_resort_services(
    resort_id: int,
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    await verify_resort_ownership(db, partner.id, resort_id)
    result = await db.execute(select(Service).where(Service.resort_id == resort_id))
    return result.scalars().all()


# ============ Room Type CRUD ============

@router.get("/room-types", response_model=List[RoomTypeOut])
async def get_all_room_types(
    resort_id: int = None,
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(RoomType)
        .join(Resort)
        .where(Resort.partner_id == partner.id)
        .options(selectinload(RoomType.images), selectinload(RoomType.offers))
    )
    if resort_id:
        query = query.where(RoomType.resort_id == resort_id)
    
    result = await db.execute(query)
    room_types = result.scalars().all()
    
    return [
        RoomTypeOut(
            id=rt.id, resort_id=rt.resort_id, name=rt.name, area=rt.area,
            quantity_standard=rt.quantity_standard, quality_standard=rt.quality_standard,
            bed_amount=rt.bed_amount, people_amount=rt.people_amount, price=rt.price,
            images=[RoomImageOut(id=img.id, url=img.url) for img in rt.images if not img.is_deleted],
            offers=[OfferOut(id=o.id, room_type_id=o.room_type_id, cost=o.cost) for o in rt.offers]
        ) for rt in room_types
    ]


@router.get("/room-types/{room_type_id}", response_model=RoomTypeOut)
async def get_room_type(
    room_type_id: int,
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    rt = await verify_room_type_ownership(db, partner.id, room_type_id)
    return RoomTypeOut(
        id=rt.id, resort_id=rt.resort_id, name=rt.name, area=rt.area,
        quantity_standard=rt.quantity_standard, quality_standard=rt.quality_standard,
        bed_amount=rt.bed_amount, people_amount=rt.people_amount, price=rt.price,
        images=[RoomImageOut(id=img.id, url=img.url) for img in rt.images if not img.is_deleted],
        offers=[OfferOut(id=o.id, room_type_id=o.room_type_id, cost=o.cost) for o in rt.offers]
    )


@router.post("/room-types", response_model=RoomTypeOut, status_code=201)
async def create_room_type(
    data: RoomTypeCreate,
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    """Tạo loại phòng mới kèm ảnh và 1 gói đặt phòng"""
    await verify_resort_ownership(db, partner.id, data.resort_id)
    
    # Tạo room type
    room_type = RoomType(
        resort_id=data.resort_id, name=data.name, area=data.area,
        quantity_standard=data.quantity_standard, quality_standard=data.quality_standard,
        bed_amount=data.bed_amount, people_amount=data.people_amount, price=data.price
    )
    db.add(room_type)
    await db.flush()
    
    # Thêm ảnh
    images = []
    for url in data.image_urls:
        img = RoomImage(room_type_id=room_type.id, url=url, is_deleted=False)
        db.add(img)
        images.append(img)
    
    # Tạo offer kèm theo
    offer = Offer(room_type_id=room_type.id, cost=data.offer.cost)
    db.add(offer)
    
    await db.commit()
    await db.refresh(offer)
    
    return RoomTypeOut(
        id=room_type.id, resort_id=room_type.resort_id, name=room_type.name, area=room_type.area,
        quantity_standard=room_type.quantity_standard, quality_standard=room_type.quality_standard,
        bed_amount=room_type.bed_amount, people_amount=room_type.people_amount, price=room_type.price,
        images=[RoomImageOut(id=img.id, url=img.url) for img in images],
        offers=[OfferOut(id=offer.id, room_type_id=offer.room_type_id, cost=offer.cost)]
    )


@router.put("/room-types/{room_type_id}", response_model=RoomTypeOut)
async def update_room_type(
    room_type_id: int,
    data: RoomTypeUpdate,
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    rt = await verify_room_type_ownership(db, partner.id, room_type_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rt, field, value)
    await db.commit()
    await db.refresh(rt)
    return RoomTypeOut(
        id=rt.id, resort_id=rt.resort_id, name=rt.name, area=rt.area,
        quantity_standard=rt.quantity_standard, quality_standard=rt.quality_standard,
        bed_amount=rt.bed_amount, people_amount=rt.people_amount, price=rt.price,
        images=[RoomImageOut(id=img.id, url=img.url) for img in rt.images if not img.is_deleted],
        offers=[OfferOut(id=o.id, room_type_id=o.room_type_id, cost=o.cost) for o in rt.offers]
    )


@router.delete("/room-types/{room_type_id}")
async def delete_room_type(
    room_type_id: int,
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    rt = await verify_room_type_ownership(db, partner.id, room_type_id)
    await db.delete(rt)
    await db.commit()
    return {"message": "Đã xóa loại phòng thành công"}


# ============ Room Images ============

@router.post("/room-types/{room_type_id}/images")
async def add_room_images(
    room_type_id: int,
    image_urls: List[str],
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    await verify_room_type_ownership(db, partner.id, room_type_id)
    images = []
    for url in image_urls:
        img = RoomImage(room_type_id=room_type_id, url=url, is_deleted=False)
        db.add(img)
        images.append(img)
    await db.commit()
    return {"message": f"Đã thêm {len(images)} ảnh", "images": [{"id": img.id, "url": img.url} for img in images]}


@router.delete("/room-types/{room_type_id}/images/{image_id}")
async def delete_room_image(
    room_type_id: int,
    image_id: int,
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    await verify_room_type_ownership(db, partner.id, room_type_id)
    result = await db.execute(select(RoomImage).where(RoomImage.id == image_id, RoomImage.room_type_id == room_type_id))
    image = result.scalars().first()
    if not image:
        raise HTTPException(status_code=404, detail="Ảnh không tồn tại")
    image.is_deleted = True
    await db.commit()
    return {"message": "Đã xóa ảnh"}


# ============ Offer CRUD ============

@router.get("/offers", response_model=List[OfferWithDetails])
async def get_all_offers(
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Offer, RoomType.name.label("rt_name"), Resort.name.label("rs_name"))
        .select_from(Offer)
        .join(RoomType, RoomType.id == Offer.room_type_id)
        .join(Resort, Resort.id == RoomType.resort_id)
        .where(Resort.partner_id == partner.id)
    )
    return [
        OfferWithDetails(
            id=r.Offer.id, room_type_id=r.Offer.room_type_id, cost=r.Offer.cost,
            room_type_name=r.rt_name, resort_name=r.rs_name,
            services=[]
        ) for r in result.all()
    ]


@router.post("/offers", response_model=OfferWithDetails, status_code=201)
async def create_offer(
    data: OfferCreate,
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    """Tạo thêm gói đặt phòng cho loại phòng đã có"""
    rt = await verify_room_type_ownership(db, partner.id, data.room_type_id)
    
    offer = Offer(room_type_id=data.room_type_id, cost=data.cost)
    db.add(offer)
    await db.commit()
    await db.refresh(offer)
    
    rs_result = await db.execute(select(Resort).where(Resort.id == rt.resort_id))
    resort = rs_result.scalars().first()
    
    return OfferWithDetails(
        id=offer.id, room_type_id=offer.room_type_id, cost=offer.cost,
        room_type_name=rt.name, resort_name=resort.name if resort else None,
        services=[]
    )


@router.put("/offers/{offer_id}", response_model=OfferWithDetails)
async def update_offer(
    offer_id: int,
    data: OfferUpdate,
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Offer)
        .select_from(Offer)
        .join(RoomType, RoomType.id == Offer.room_type_id)
        .join(Resort, Resort.id == RoomType.resort_id)
        .where(Offer.id == offer_id, Resort.partner_id == partner.id)
    )
    offer = result.scalars().first()
    if not offer:
        raise HTTPException(status_code=404, detail="Gói đặt phòng không tồn tại")
    
    if data.cost is not None:
        offer.cost = data.cost
    
    await db.commit()
    
    result = await db.execute(
        select(Offer, RoomType.name.label("rt_name"), Resort.name.label("rs_name"))
        .select_from(Offer)
        .join(RoomType, RoomType.id == Offer.room_type_id)
        .join(Resort, Resort.id == RoomType.resort_id)
        .where(Offer.id == offer_id)
    )
    r = result.first()
    return OfferWithDetails(
        id=r.Offer.id, room_type_id=r.Offer.room_type_id, cost=r.Offer.cost,
        room_type_name=r.rt_name, resort_name=r.rs_name,
        services=[]
    )


@router.delete("/offers/{offer_id}")
async def delete_offer(
    offer_id: int,
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Offer)
        .select_from(Offer)
        .join(RoomType, RoomType.id == Offer.room_type_id)
        .join(Resort, Resort.id == RoomType.resort_id)
        .where(Offer.id == offer_id, Resort.partner_id == partner.id)
    )
    offer = result.scalars().first()
    if not offer:
        raise HTTPException(status_code=404, detail="Gói đặt phòng không tồn tại")
    await db.delete(offer)
    await db.commit()
    return {"message": "Đã xóa gói đặt phòng thành công"}

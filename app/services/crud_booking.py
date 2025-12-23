from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
from fastapi import HTTPException

from app.models.booking import Booking
from app.models.booking_detail import BookingDetail
from app.models.offer import Offer
from app.schemas.booking import BookingDetailCreate


async def get_latest_unpaid_cart(db: AsyncSession, customer_id: int):
    """Lấy giỏ hàng mới nhất chưa thanh toán"""
    result = await db.execute(
        select(Booking)
        .filter(Booking.customer_id == customer_id, Booking.status == "pending")
        .order_by(Booking.created_at.desc())
    )
    return result.scalars().first()


async def create_cart(db: AsyncSession, customer_id: int) -> Booking:
    """Tạo giỏ hàng mới (Booking với status pending)"""
    new_cart = Booking(
        customer_id=customer_id,
        status="pending",
        cost=Decimal("0")
    )
    db.add(new_cart)
    await db.commit()
    await db.refresh(new_cart)
    return new_cart


async def get_or_create_cart(db: AsyncSession, customer_id: int) -> Booking:
    """Lấy giỏ hàng hiện có hoặc tạo mới nếu chưa có"""
    cart = await get_latest_unpaid_cart(db, customer_id)
    if not cart:
        cart = await create_cart(db, customer_id)
    return cart


async def add_booking_detail(db: AsyncSession, booking_id: int, booking_detail: BookingDetailCreate):
    """Thêm BookingDetail vào Booking"""
    from sqlalchemy.orm import selectinload
    
    # Lấy Offer kèm RoomType để lấy giá
    result = await db.execute(
        select(Offer)
        .filter(Offer.id == booking_detail.offer_id)
        .options(selectinload(Offer.room_type))
    )
    offer = result.scalar_one_or_none()
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer không tồn tại")
    
    # Ưu tiên lấy giá từ Offer, nếu không có thì lấy từ RoomType
    if offer.cost:
        offer_price = offer.cost
    elif offer.room_type and offer.room_type.price:
        offer_price = offer.room_type.price
    else:
        offer_price = Decimal("0")
    
    item_cost = booking_detail.number_of_rooms * offer_price

    new_booking_detail = BookingDetail(
        booking_id=booking_id,
        offer_id=booking_detail.offer_id,
        number_of_rooms=booking_detail.number_of_rooms,
        started_at=booking_detail.started_at,
        finished_at=booking_detail.finished_at,
        status=booking_detail.status,
        cost=item_cost
    )
    db.add(new_booking_detail)
    await db.flush()

    # Cập nhật tổng cost của Booking
    result = await db.execute(select(Booking).filter(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if booking:
        if booking.cost is None:
            booking.cost = Decimal("0")
        booking.cost += new_booking_detail.cost

    await db.commit()
    await db.refresh(new_booking_detail)
    return new_booking_detail

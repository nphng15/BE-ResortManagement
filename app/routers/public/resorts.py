from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import Optional

from app.db_async import get_db
from app.models.account import Account
from app.models.customer import Customer
from app.models.feedback import Feedback
from app.models.resort import Resort
from app.models.resort_images import ResortImage
from app.models.room_type import RoomType
from app.models.room import Room
from app.models.offer import Offer
from app.models.booking_detail import BookingDetail
from app.models.booking_timeslot import BookingTimeSlot
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.dependencies.auth import get_current_account

router = APIRouter(prefix="/api/v1", tags=["Resorts"])

@router.get("/resorts")
async def get_resort_detail(
    id: int = Query(...),
    checkin: Optional[str] = Query(None),
    checkout: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    # Parse checkin/checkout dates
    if checkin is None:
        checkin_date = datetime.now()
    else:
        try:
            checkin_date = datetime.fromisoformat(checkin)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for checkin, use YYYY-MM-DD")

    if checkout is None:
        checkout_date = checkin_date + timedelta(days=1)
    else:
        try:
            checkout_date = datetime.fromisoformat(checkout)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for checkout, use YYYY-MM-DD")

    resort_result = await db.execute(select(Resort).where(Resort.id == id))
    resort = resort_result.scalar_one_or_none()

    if not resort:
        raise HTTPException(status_code=404, detail="Resort not found")

    img_result = await db.execute(
        select(ResortImage.url).where(ResortImage.resort_id == id)
    )
    images = [row[0] for row in img_result.all()]

    roomtype_result = await db.execute(
        select(
            RoomType.id,
            RoomType.name,
            RoomType.area,
            RoomType.bed_amount,
            RoomType.people_amount,
            RoomType.price
        ).where(RoomType.resort_id == id)
    )
    room_types_data = roomtype_result.all()

    room_types = []
    for r in room_types_data:
        # Count total rooms for this room type
        total_rooms_result = await db.execute(
            select(func.count(Room.id)).where(Room.room_type_id == r.id)
        )
        total_rooms = total_rooms_result.scalar() or 0

        # Count booked rooms in the date range
        booked_rooms_subq = (
            select(BookingTimeSlot.room_id)
            .join(Room, Room.id == BookingTimeSlot.room_id)
            .where(
                and_(
                    Room.room_type_id == r.id,
                    BookingTimeSlot.started_time < checkout_date,
                    BookingTimeSlot.finished_time > checkin_date
                )
            )
            .distinct()
        )
        booked_rooms_result = await db.execute(
            select(func.count()).select_from(booked_rooms_subq.subquery())
        )
        booked_rooms = booked_rooms_result.scalar() or 0

        available_rooms = total_rooms - booked_rooms

        room_types.append({
            "id": r.id,
            "name": r.name,
            "area": float(r.area),
            "bed_amount": r.bed_amount,
            "people_amount": r.people_amount,
            "price": float(r.price),
            "available_rooms": available_rooms
        })

    return {
        "id": resort.id,
        "name": resort.name,
        "address": resort.address,
        "rating": resort.rating,
        "images": images,
        "room_types": room_types
    }

@router.get("/resorts/{id}/feedbacks")
async def get_feedbacks(id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Feedback)
        .where(Feedback.resort_id == id)
        .options(
            selectinload(Feedback.customer).selectinload(Customer.account)
        )
        .order_by(Feedback.created_at.desc())
    )
    result = await db.execute(stmt)
    feedbacks = result.scalars().all()
    if not feedbacks:
        return []
    
    response = []
    for fb in feedbacks:
        username = None
        if fb.customer and fb.customer.account:
            username = fb.customer.account.username
        
        response.append({
            "id": fb.id,
            "resort_id": fb.resort_id,
            "customer_id": fb.customer_id,
            "rating": fb.rating,
            "comment": fb.comment,
            "created_at": fb.created_at,
            "username": username
        })
    
    return response

@router.post("/resorts/{id}/feedbacks", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def add_feedback(
    id: int,
    feedback: FeedbackCreate,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db)
):
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    has_booking = (await db.execute(
        select(BookingDetail.id)
        .join(Offer, BookingDetail.offer_id == Offer.id)
        .join(RoomType, Offer.room_type_id == RoomType.id)
        .where(
            RoomType.resort_id == id,
            BookingDetail.status == "PAID"
        )
        .join(BookingDetail.booking)
        .where(BookingDetail.booking.has(customer_id=customer_id))
        .limit(1)
    )).scalar_one_or_none()

    if not has_booking:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chỉ có thể đánh giá resort mà bạn đã từng đặt phòng"
        )

    new_feedback = Feedback(
        resort_id=id,
        customer_id=customer_id,
        rating=feedback.rating,
        comment=feedback.comment
    )
    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)
    return new_feedback

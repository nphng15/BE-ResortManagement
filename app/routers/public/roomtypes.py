from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Optional

from app.db_async import get_db
from app.models.room_type import RoomType
from app.models.room import Room
from app.models.offer import Offer
from app.models.room_images import RoomImage
from app.models.booking_timeslot import BookingTimeSlot

router = APIRouter(prefix="/api/v1", tags=["RoomType"])

class RoomTypeRequest(BaseModel):
    room_type_ids: list[int]
    checkin: Optional[str] = None
    checkout: Optional[str] = None


@router.post("/roomtypes/details")
async def get_roomtype_details(
    payload: RoomTypeRequest,
    db: AsyncSession = Depends(get_db)
):
    if not payload.room_type_ids:
        raise HTTPException(status_code=400, detail="room_type_ids cannot be empty")

    # Parse checkin/checkout dates
    if payload.checkin is None:
        checkin_date = datetime.now()
    else:
        try:
            checkin_date = datetime.fromisoformat(payload.checkin)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for checkin, use YYYY-MM-DD")

    if payload.checkout is None:
        checkout_date = checkin_date + timedelta(days=1)
    else:
        try:
            checkout_date = datetime.fromisoformat(payload.checkout)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for checkout, use YYYY-MM-DD")

    stmt = select(
        RoomType.id,
        RoomType.name,
        RoomType.area,
        RoomType.people_amount,
        RoomType.price
    ).where(RoomType.id.in_(payload.room_type_ids))

    result = await db.execute(stmt)
    room_types = result.all()

    if not room_types:
        raise HTTPException(status_code=404, detail="No room types found")

    output = []

    for rt in room_types:
        # Count total rooms for this room type
        total_rooms_result = await db.execute(
            select(func.count(Room.id)).where(Room.room_type_id == rt.id)
        )
        total_rooms = total_rooms_result.scalar() or 0

        # Count booked rooms in the date range
        booked_rooms_subq = (
            select(BookingTimeSlot.room_id)
            .join(Room, Room.id == BookingTimeSlot.room_id)
            .where(
                and_(
                    Room.room_type_id == rt.id,
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

        offers_result = await db.execute(
            select(Offer.id, Offer.cost)
            .where(Offer.room_type_id == rt.id)
        )
        offers = [{"id": o.id, "cost": float(o.cost)} for o in offers_result.all()]

        img_result = await db.execute(
            select(RoomImage.url)
            .where(RoomImage.room_type_id == rt.id, RoomImage.is_deleted == False)
        )
        images = [row[0] for row in img_result.all()]

        output.append({
            "id": rt.id,
            "name": rt.name,
            "area": float(rt.area),
            "people_amount": rt.people_amount,
            "price": float(rt.price),
            "available_rooms": available_rooms,
            "offers": offers,
            "images": images
        })

    return output

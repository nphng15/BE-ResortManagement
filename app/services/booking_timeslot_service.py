from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, delete
from fastapi import HTTPException

from app.models.booking_timeslot import BookingTimeSlot
from app.models.booking_detail import BookingDetail
from app.models.room import Room
from app.models.offer import Offer


async def check_room_availability(
    db: AsyncSession, 
    offer_id: int, 
    number_of_rooms: int, 
    started_at, 
    finished_at
) -> dict:
    """
    Kiểm tra số phòng còn trống trong khoảng thời gian.
    Trả về dict với available_rooms và is_available.
    """
    # Lấy room_type_id từ offer
    offer_result = await db.execute(select(Offer).filter(Offer.id == offer_id))
    offer = offer_result.scalar_one_or_none()
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer không tồn tại")
    
    room_type_id = offer.room_type_id

    # Đếm tổng số phòng của room_type này
    total_rooms_result = await db.execute(
        select(func.count(Room.id)).where(Room.room_type_id == room_type_id)
    )
    total_rooms = total_rooms_result.scalar() or 0

    # Đếm số phòng đã bị book trong khoảng thời gian này
    booked_rooms_result = await db.execute(
        select(func.count(BookingTimeSlot.room_id.distinct()))
        .select_from(BookingTimeSlot)
        .join(Room, Room.id == BookingTimeSlot.room_id)
        .where(
            and_(
                Room.room_type_id == room_type_id,
                BookingTimeSlot.started_time < finished_at,
                BookingTimeSlot.finished_time > started_at
            )
        )
    )
    booked_rooms = booked_rooms_result.scalar() or 0

    available_rooms = total_rooms - booked_rooms

    return {
        "total_rooms": total_rooms,
        "booked_rooms": booked_rooms,
        "available_rooms": available_rooms,
        "is_available": available_rooms >= number_of_rooms
    }


async def validate_room_availability(
    db: AsyncSession, 
    offer_id: int, 
    number_of_rooms: int, 
    started_at, 
    finished_at
):
    """
    Validate và raise exception nếu không đủ phòng trống.
    """
    availability = await check_room_availability(
        db, offer_id, number_of_rooms, started_at, finished_at
    )
    
    if not availability["is_available"]:
        raise HTTPException(
            status_code=400,
            detail=f"Không đủ phòng trống trong khung giờ này. Cần {number_of_rooms} phòng, chỉ còn {availability['available_rooms']} phòng."
        )
    
    return availability


async def create_booking_timeslots(db: AsyncSession, booking_detail: BookingDetail, invoice_id: int = None):
    """
    Tạo BookingTimeSlot cho các phòng được book.
    Chọn các phòng trống trong khoảng thời gian booking và đánh dấu là bận.
    """
    room_type_id = booking_detail.offer.room_type_id
    number_of_rooms = booking_detail.number_of_rooms
    started_at = booking_detail.started_at
    finished_at = booking_detail.finished_at

    # Lấy danh sách room_id đã bị book trong khoảng thời gian này
    booked_rooms_subq = (
        select(BookingTimeSlot.room_id)
        .where(
            and_(
                BookingTimeSlot.started_time < finished_at,
                BookingTimeSlot.finished_time > started_at
            )
        )
    )

    # Lấy các phòng trống thuộc room_type này
    available_rooms_result = await db.execute(
        select(Room)
        .where(
            Room.room_type_id == room_type_id,
            Room.id.notin_(booked_rooms_subq)
        )
        .limit(number_of_rooms)
    )
    available_rooms = available_rooms_result.scalars().all()

    if len(available_rooms) < number_of_rooms:
        raise HTTPException(
            status_code=400,
            detail=f"Không đủ phòng trống. Cần {number_of_rooms} phòng, chỉ còn {len(available_rooms)} phòng."
        )

    # Tạo BookingTimeSlot cho từng phòng
    created_timeslots = []
    for room in available_rooms:
        timeslot = BookingTimeSlot(
            room_id=room.id,
            started_time=started_at,
            finished_time=finished_at,
            invoice_id=invoice_id
        )
        db.add(timeslot)
        created_timeslots.append(timeslot)

    return created_timeslots


async def delete_booking_timeslots_by_invoice(db: AsyncSession, invoice_id: int):
    """
    Xóa tất cả BookingTimeSlot theo invoice_id khi hủy booking.
    Giải phóng phòng để người khác có thể đặt.
    """
    await db.execute(
        delete(BookingTimeSlot).where(BookingTimeSlot.invoice_id == invoice_id)
    )


async def delete_booking_timeslots_by_booking_detail(db: AsyncSession, booking_detail_id: int):
    """
    Xóa tất cả BookingTimeSlot theo booking_detail_id khi hủy booking.
    Giải phóng phòng để người khác có thể đặt.
    """
    from app.models.invoice import Invoice
    
    # Lấy tất cả invoice_ids của booking_detail này
    invoice_result = await db.execute(
        select(Invoice.id).filter(Invoice.booking_detail_id == booking_detail_id)
    )
    invoice_ids = [row[0] for row in invoice_result.fetchall()]
    
    if invoice_ids:
        await db.execute(
            delete(BookingTimeSlot).where(BookingTimeSlot.invoice_id.in_(invoice_ids))
        )

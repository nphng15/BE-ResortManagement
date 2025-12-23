from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import BookingDetail, Invoice
from app.models.account import Account
from app.models.offer import Offer
from app.models.room_type import RoomType
from app.models.resort import Resort
from app.db_async import get_db
from app.dependencies.auth import get_current_account
from app.services.booking_timeslot_service import delete_booking_timeslots_by_booking_detail

router = APIRouter(prefix="/api/v1/customer", tags=["Resorts"])

@router.get("/{id}/histories")
async def get_booking_histories(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(BookingDetail)
        .join(Invoice, (Invoice.booking_detail_id == BookingDetail.id) & (Invoice.customer_id == id))
        .filter(BookingDetail.status.in_(["PAID", "CANCELLED"]))
        .options(
            selectinload(BookingDetail.offer)
            .selectinload(Offer.room_type)
            .selectinload(RoomType.resort)
        )
        .distinct()
    )

    booking_details = result.scalars().all()

    if not booking_details:
        raise HTTPException(status_code=404, detail="No booking histories found for this customer")

    histories = []
    for detail in booking_details:
        offer = detail.offer
        room_type = offer.room_type if offer else None
        resort = room_type.resort if room_type else None
        
        histories.append({
            "id": detail.id,
            "booking_id": detail.booking_id,
            "cost": float(detail.cost) if detail.cost else 0,
            "number_of_rooms": detail.number_of_rooms,
            "started_at": detail.started_at,
            "finished_at": detail.finished_at,
            "status": detail.status,
            "room_type_name": room_type.name if room_type else None,
            "room_type_id": room_type.id if room_type else None,
            "resort_name": resort.name if resort else None,
            "resort_id": resort.id if resort else None,
        })

    return histories



@router.delete("/booking-detail/{booking_detail_id}")
async def cancel_booking_detail(
    booking_detail_id: int,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db)
):
    """
    Hủy một phòng cụ thể theo booking_detail_id.
    Chỉ hủy đúng phòng mà user chọn, không ảnh hưởng các phòng khác.
    """
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    # Tìm booking_detail và kiểm tra quyền sở hữu qua invoice
    result = await db.execute(
        select(BookingDetail)
        .join(Invoice, Invoice.booking_detail_id == BookingDetail.id)
        .filter(
            BookingDetail.id == booking_detail_id,
            Invoice.customer_id == customer_id,
            BookingDetail.status == "PAID"
        )
        .options(
            selectinload(BookingDetail.offer)
            .selectinload(Offer.room_type)
            .selectinload(RoomType.resort)
        )
    )
    booking_detail = result.scalar_one_or_none()

    if not booking_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking detail hoặc bạn không có quyền hủy"
        )

    # Cập nhật status thành CANCELLED
    booking_detail.status = "CANCELLED"

    # Xóa BookingTimeSlot để giải phóng phòng
    await delete_booking_timeslots_by_booking_detail(db, booking_detail_id)

    await db.commit()

    offer = booking_detail.offer
    room_type = offer.room_type if offer else None
    resort = room_type.resort if room_type else None

    return {
        "message": "Hủy phòng thành công",
        "booking_detail": {
            "id": booking_detail.id,
            "booking_id": booking_detail.booking_id,
            "cost": float(booking_detail.cost) if booking_detail.cost else 0,
            "number_of_rooms": booking_detail.number_of_rooms,
            "started_at": booking_detail.started_at,
            "finished_at": booking_detail.finished_at,
            "status": booking_detail.status,
            "room_type_name": room_type.name if room_type else None,
            "resort_name": resort.name if resort else None,
        }
    }

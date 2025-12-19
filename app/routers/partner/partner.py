from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import extract, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

from app.models.account import Account
from app.models.booking_detail import BookingDetail
from app.models.booking_timeslot import BookingTimeSlot
from app.models.invoice import Invoice
from app.models.number_of_room import BookingDetailUpdate
from app.models.partner import Partner
from app.models.resort import Resort
from app.models.room import Room
from app.models.room_type import RoomType
from app.models.withdraw import Withdraw
from app.schemas.booking import BookingDetailCreate
from app.database import get_db
from app.schemas.payment import PaymentRequest
from app.services import crud_booking as crud
from app.dependencies.auth import get_current_partner

router = APIRouter(prefix="/api/v1", tags=["Partners"])

@router.get("/resorts/{id}/partner")
def get_partner_of_resort(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = db.execute(
        select(Partner)
        .join(Resort, Resort.partner_id == Partner.id)
        .where(Resort.id == id)
        .options(selectinload(Partner.account))
    )

    partner = result.scalars().first()

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found for the resort")

    # Trả về thông tin cơ bản
    return {
        "name": partner.name,
        "address": partner.address,
        "phone_number": getattr(partner, "phone_number", None)
    }

@router.get("/partner/bookings/schedule")
def get_partner_booking_schedule(
    start: date | None = Query(None, description="Ngày bắt đầu hiển thị lịch (YYYY-MM-DD)"),
    end: date | None = Query(None, description="Ngày kết thúc hiển thị lịch (YYYY-MM-DD)"),
    resort_id: int | None = Query(None, description="Lọc theo resort cụ thể"),
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách lịch đặt phòng (BookingTimeSlot) của partner trong khoảng thời gian cụ thể.
    Nếu không truyền start/end → mặc định là từ Thứ 2 đến Chủ Nhật của tuần hiện tại.
    """
    partner_id = partner.id

    # 🕓 Nếu không truyền start/end, tự động tính khoảng tuần hiện tại
    if not start or not end:
        today = datetime.utcnow().date()
        start_of_week = today - timedelta(days=today.weekday())  # Thứ 2
        end_of_week = start_of_week + timedelta(days=6)          # Chủ nhật
        start = start_of_week
        end = end_of_week
    
    # Convert date to datetime for query
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())

    query = (
        select(
            BookingTimeSlot.room_id,
            BookingTimeSlot.started_time,
            BookingTimeSlot.finished_time,
            Room.number.label("room_number"),
            RoomType.name.label("room_type_name"),
            Resort.name.label("resort_name"),
        )
        .join(Room, Room.id == BookingTimeSlot.room_id)
        .join(RoomType, RoomType.id == Room.room_type_id)
        .join(Resort, Resort.id == RoomType.resort_id)
        .where(Resort.partner_id == partner_id)
        .where(
            BookingTimeSlot.finished_time >= start_dt,
            BookingTimeSlot.started_time <= end_dt
        )
        .order_by(BookingTimeSlot.started_time.asc())
    )

    if resort_id:
        query = query.where(Resort.id == resort_id)

    result = db.execute(query)
    slots = result.all()

    return [
        {
            "room_id": s.room_id,
            "resort_name": s.resort_name,
            "room_type": s.room_type_name,
            "room_number": s.room_number,
            "started_time": s.started_time,
            "finished_time": s.finished_time
        }
        for s in slots
    ]


@router.get("/partner/statistics")
def get_partner_statistics(
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    partner_id = partner.id

    # 2️⃣ Số lượt đặt mới trong ngày
    today = date.today()
    result_new = db.execute(
        select(func.count(Invoice.id)).where(
            Invoice.partner_id == partner_id,
            func.date(Invoice.finished_time) == today
        )
    )
    new_bookings_today = result_new.scalar() or 0

    # 3️⃣ Doanh thu tháng này
    now = datetime.utcnow()
    result_month = db.execute(
        select(func.sum(Invoice.cost)).where(
            Invoice.partner_id == partner_id,
            extract('month', Invoice.finished_time) == now.month,
            extract('year', Invoice.finished_time) == now.year
        )
    )
    monthly_revenue = result_month.scalar() or 0

    # 4️⃣ Tổng số lượt đặt
    result_total = db.execute(
        select(func.count(Invoice.id)).where(Invoice.partner_id == partner_id)
    )
    total_bookings = result_total.scalar() or 0

    # 5️⃣ Số dư hiện tại
    current_balance = float(partner.balance or 0)

    # 6️⃣ Biến động số dư
    # Doanh thu (Invoice)
    revenue_result = db.execute(
        select(
            Invoice.id.label("invoice_id"),
            Invoice.booking_detail_id,
            Invoice.cost.label("amount"),
            Invoice.finished_time.label("time")
        ).where(Invoice.partner_id == partner_id)
        .order_by(Invoice.finished_time.desc())
    )
    revenues = [
        {
            "invoice_id": row.invoice_id,
            "booking_detail_id": row.booking_detail_id,
            "amount": float(row.amount),
            "time": row.time,
            "type": "REVENUE"
        }
        for row in revenue_result.all()
    ]

    # Rút tiền (Withdrawals)
    withdrawal_result = db.execute(
        select(
            Withdraw.id,
            Withdraw.transaction_amount.label("amount"),
            Withdraw.created_at
        ).where(Withdraw.partner_id == partner_id)
        .order_by(Withdraw.created_at.desc())
    )
    withdrawals = [
        {
            "id": row.id,
            "amount": float(row.amount),
            "time": row.created_at,
            "type": "WITHDRAW"
        }
        for row in withdrawal_result.all()
    ]

    return {
        "new_bookings_today": new_bookings_today,
        "monthly_revenue": float(monthly_revenue),
        "total_bookings": total_bookings,
        "current_balance": current_balance,
        "balance_movements": {
            "revenues": revenues,
            "withdrawals": withdrawals
        }
    }

@router.post("/partner/withdraw")
def create_withdraw_request(
    amount: float = Query(..., gt=0, description="Số tiền muốn rút"),
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    partner_id = partner.id
    
    # Kiểm tra số dư
    balance = partner.balance or 0
    if Decimal(balance) < Decimal(amount):
        raise HTTPException(status_code=400, detail="Số dư không đủ để rút tiền")

    # Tạo yêu cầu rút tiền
    withdraw_request = Withdraw(
        partner_id=partner_id,
        transaction_amount=Decimal(amount),
        created_at=datetime.utcnow(),
        status="PENDING"
    )

    # Trừ số dư ngay (hoặc có thể đợi admin duyệt mới trừ)
    partner.balance = Decimal(balance) - Decimal(amount)

    db.add(withdraw_request)
    db.add(partner)
    db.commit()
    db.refresh(withdraw_request)

    return {
        "message": "Yêu cầu rút tiền đã được tạo thành công",
        "withdraw_id": withdraw_request.id,
        "partner_id": partner_id,
        "requested_amount": float(amount),
        "remaining_balance": float(partner.balance),
        "status": withdraw_request.status,
        "created_at": withdraw_request.created_at
    }
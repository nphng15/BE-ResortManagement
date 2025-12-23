from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import extract, func, select
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta

from app.models.account import Account
from app.models.booking_detail import BookingDetail
from app.models.booking_timeslot import BookingTimeSlot
from app.models.invoice import Invoice
from app.models.partner import Partner
from app.models.resort import Resort
from app.models.room import Room
from app.models.room_type import RoomType
from app.models.withdraw import Withdraw
from app.db_async import get_db
from app.dependencies.auth import get_current_partner

router = APIRouter(prefix="/api/v1", tags=["Partners"])

@router.get("/resorts/{id}/partner")
async def get_partner_of_resort(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Partner)
        .join(Resort, Resort.partner_id == Partner.id)
        .where(Resort.id == id)
        .options(selectinload(Partner.account))
    )

    partner = result.scalars().first()

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found for the resort")

    return {
        "name": partner.name,
        "address": partner.address,
        "phone_number": getattr(partner, "phone_number", None)
    }


@router.get("/partner/bookings/schedule")
async def get_partner_booking_schedule(
    start: date | None = Query(None),
    end: date | None = Query(None),
    resort_id: int | None = Query(None),
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    partner_id = partner.id

    if not start or not end:
        today = datetime.utcnow().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        start = start_of_week
        end = end_of_week
    
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
        .where(BookingTimeSlot.finished_time >= start_dt, BookingTimeSlot.started_time <= end_dt)
        .order_by(BookingTimeSlot.started_time.asc())
    )

    if resort_id:
        query = query.where(Resort.id == resort_id)

    result = await db.execute(query)
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
async def get_partner_statistics(
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    partner_id = partner.id

    today = date.today()
    result_new = await db.execute(
        select(func.count(Invoice.id)).where(
            Invoice.partner_id == partner_id,
            func.date(Invoice.finished_time) == today
        )
    )
    new_bookings_today = result_new.scalar() or 0

    now = datetime.utcnow()
    result_month = await db.execute(
        select(func.sum(Invoice.cost)).where(
            Invoice.partner_id == partner_id,
            extract('month', Invoice.finished_time) == now.month,
            extract('year', Invoice.finished_time) == now.year
        )
    )
    monthly_revenue = result_month.scalar() or 0

    result_total = await db.execute(
        select(func.count(Invoice.id)).where(Invoice.partner_id == partner_id)
    )
    total_bookings = result_total.scalar() or 0

    current_balance = float(partner.balance or 0)

    revenue_result = await db.execute(
        select(
            Invoice.id.label("invoice_id"),
            Invoice.booking_detail_id,
            Invoice.cost.label("amount"),
            Invoice.finished_time.label("time")
        ).where(Invoice.partner_id == partner_id)
        .order_by(Invoice.finished_time.desc())
    )
    revenues = [
        {"invoice_id": row.invoice_id, "booking_detail_id": row.booking_detail_id, "amount": float(row.amount), "time": row.time, "type": "REVENUE"}
        for row in revenue_result.all()
    ]

    withdrawal_result = await db.execute(
        select(Withdraw.id, Withdraw.transaction_amount.label("amount"), Withdraw.created_at, Withdraw.status)
        .where(Withdraw.partner_id == partner_id)
        .order_by(Withdraw.created_at.desc())
    )
    withdrawals = [
        {"id": row.id, "amount": float(row.amount), "time": row.created_at, "status": row.status, "type": "WITHDRAW"}
        for row in withdrawal_result.all()
    ]

    return {
        "new_bookings_today": new_bookings_today,
        "monthly_revenue": float(monthly_revenue),
        "total_bookings": total_bookings,
        "current_balance": current_balance,
        "balance_movements": {"revenues": revenues, "withdrawals": withdrawals}
    }

@router.post("/partner/withdraw")
async def create_withdraw_request(
    amount: float = Query(..., gt=0),
    partner: Partner = Depends(get_current_partner),
    db: AsyncSession = Depends(get_db)
):
    balance = partner.balance or 0
    if Decimal(balance) < Decimal(amount):
        raise HTTPException(status_code=400, detail="Số dư không đủ để rút tiền")

    withdraw_request = Withdraw(
        partner_id=partner.id,
        transaction_amount=Decimal(amount),
        created_at=datetime.utcnow(),
        status="PENDING"
    )

    partner.balance = Decimal(balance) - Decimal(amount)

    db.add(withdraw_request)
    db.add(partner)
    await db.commit()
    await db.refresh(withdraw_request)

    return {
        "message": "Yêu cầu rút tiền đã được tạo thành công",
        "withdraw_id": withdraw_request.id,
        "partner_id": partner.id,
        "requested_amount": float(amount),
        "remaining_balance": float(partner.balance),
        "status": withdraw_request.status,
        "created_at": withdraw_request.created_at
    }

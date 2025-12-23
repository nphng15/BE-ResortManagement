from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, date
from app.models import Partner
from app.models.account import Account
from app.models.withdraw import Withdraw
from app.db_async import get_db
from app.dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Withdraw Management"])

@router.get("/withdraws")
async def get_withdraw_requests(
    current_admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    status: str | None = Query(None, description="Lọc theo trạng thái: PENDING/APPROVED/REJECTED"),
    partner_id: int | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None)
):
    # Base query
    query = select(Withdraw, Partner.name).join(Partner, Withdraw.partner_id == Partner.id)

    filters = []
    if status:
        filters.append(func.upper(Withdraw.status) == status.upper())
    if partner_id:
        filters.append(Withdraw.partner_id == partner_id)
    if start_date:
        filters.append(Withdraw.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        filters.append(Withdraw.created_at <= datetime.combine(end_date, datetime.max.time()))

    if filters:
        query = query.where(and_(*filters))

    # Count tổng số bản ghi
    count_query = select(func.count()).select_from(Withdraw)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Lấy dữ liệu trang hiện tại
    result = await db.execute(
        query.order_by(Withdraw.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    withdraws = result.all()

    data = [
        {
            "id": w.Withdraw.id,
            "partner_id": w.Withdraw.partner_id,
            "partner_name": w.name,
            "transaction_amount": float(w.Withdraw.transaction_amount),
            "status": w.Withdraw.status,
            "created_at": w.Withdraw.created_at,
            "finished_at": w.Withdraw.finished_at
        }
        for w in withdraws
    ]

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "data": data
    }


@router.put("/withdraws/{id}")
async def process_withdraw_request(
    id: int,
    action: str = Query(..., description="Hành động: APPROVE hoặc REJECT"),
    current_admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Duyệt hoặc từ chối yêu cầu rút tiền"""
    action = action.upper()
    if action not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Action must be APPROVE or REJECT")

    result = await db.execute(select(Withdraw).where(Withdraw.id == id))
    withdraw = result.scalar_one_or_none()

    if not withdraw:
        raise HTTPException(status_code=404, detail="Withdraw request not found")

    if withdraw.status.upper() != "PENDING":
        raise HTTPException(status_code=400, detail=f"Cannot process withdraw in status '{withdraw.status}'")

    if action == "APPROVE":
        withdraw.status = "APPROVED"
        message = "Withdraw request approved successfully"
    else:
        # Hoàn tiền về balance của partner
        partner_result = await db.execute(select(Partner).where(Partner.id == withdraw.partner_id))
        partner = partner_result.scalar_one_or_none()
        if partner:
            partner.balance = (partner.balance or 0) + withdraw.transaction_amount
            db.add(partner)
        withdraw.status = "REJECTED"
        message = "Withdraw request rejected, amount refunded to partner balance"

    withdraw.finished_at = datetime.utcnow()
    db.add(withdraw)
    await db.commit()
    await db.refresh(withdraw)

    return {
        "message": message,
        "withdraw_id": withdraw.id,
        "partner_id": withdraw.partner_id,
        "amount": float(withdraw.transaction_amount),
        "status": withdraw.status,
        "finished_at": withdraw.finished_at
    }

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db_async import get_db
from app.models.account import Account
from app.schemas.auth import PartnerApprovalRequest, PartnerApprovalResponse, PartnerResponse
from app.services.auth_service import get_pending_partners, approve_partner
from app.dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/v1/admin/partners", tags=["Admin Partner Management"])


@router.get("/pending", response_model=List[PartnerResponse])
async def get_pending_partner_requests(
    current_admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách đối tác đang chờ duyệt"""
    pending_list = await get_pending_partners(db)
    
    return [
        PartnerResponse(
            id=partner.id,
            account_id=partner.account_id,
            name=partner.name,
            phone_number=partner.phone_number,
            address=partner.address,
            banking_number=partner.banking_number,
            bank=partner.bank,
            account_status=account.status
        )
        for partner, account in pending_list
    ]


@router.post("/approve", response_model=PartnerApprovalResponse)
async def approve_partner_request(
    request: PartnerApprovalRequest,
    current_admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Duyệt hoặc từ chối yêu cầu đăng ký đối tác"""
    account = await approve_partner(db, request.account_id, request.approved)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending partner account not found"
        )
    
    action = "approved" if request.approved else "rejected"
    return PartnerApprovalResponse(
        message=f"Partner registration {action} successfully",
        account_id=account.account_id,
        status=account.status
    )

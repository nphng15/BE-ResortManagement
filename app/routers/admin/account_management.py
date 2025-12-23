from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from pydantic import BaseModel

from app.db_async import get_db
from app.models.account import Account
from app.models.customer import Customer
from app.models.partner import Partner
from app.dependencies.auth import get_current_admin


router = APIRouter(prefix="/api/v1/admin/accounts", tags=["Admin Account Management"])


class BanAccountRequest(BaseModel):
    account_id: int
    reason: Optional[str] = None


class BanAccountResponse(BaseModel):
    message: str
    account_id: int
    status: str


class AccountListResponse(BaseModel):
    account_id: int
    username: str
    status: str
    account_type: str
    name: Optional[str] = None
    phone_number: Optional[str] = None


@router.get("", response_model=list[AccountListResponse])
async def get_accounts(
    current_admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    account_type: Optional[str] = Query(None, description="Lọc theo loại: CUSTOMER hoặc PARTNER"),
    status: Optional[str] = Query(None, description="Lọc theo trạng thái: ACTIVE, BANNED"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo username hoặc tên"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100)
):
    """Lấy danh sách tài khoản khách hàng và đối tác"""
    results = []
    
    # Query customers
    if account_type is None or account_type.upper() == "CUSTOMER":
        customer_query = (
            select(Account, Customer)
            .join(Customer, Account.account_id == Customer.account_id)
            .where(Account.is_deleted == False)
        )
        
        if status:
            customer_query = customer_query.where(Account.status == status.upper())
        
        if search:
            customer_query = customer_query.where(
                or_(
                    Account.username.ilike(f"%{search}%"),
                    Customer.fullname.ilike(f"%{search}%")
                )
            )
        
        customers = (await db.execute(customer_query)).all()
        for account, customer in customers:
            results.append(AccountListResponse(
                account_id=account.account_id,
                username=account.username,
                status=account.status,
                account_type="CUSTOMER",
                name=customer.fullname,
                phone_number=customer.phone_number
            ))
    
    # Query partners
    if account_type is None or account_type.upper() == "PARTNER":
        partner_query = (
            select(Account, Partner)
            .join(Partner, Account.account_id == Partner.account_id)
            .where(Account.is_deleted == False)
        )
        
        if status:
            partner_query = partner_query.where(Account.status == status.upper())
        
        if search:
            partner_query = partner_query.where(
                or_(
                    Account.username.ilike(f"%{search}%"),
                    Partner.name.ilike(f"%{search}%")
                )
            )
        
        partners = (await db.execute(partner_query)).all()
        for account, partner in partners:
            results.append(AccountListResponse(
                account_id=account.account_id,
                username=account.username,
                status=account.status,
                account_type="PARTNER",
                name=partner.name,
                phone_number=partner.phone_number
            ))
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    
    return results[start:end]


@router.post("/ban", response_model=BanAccountResponse)
async def ban_account(
    request: BanAccountRequest,
    current_admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Cấm tài khoản khách hàng hoặc đối tác"""
    account = (await db.execute(
        select(Account)
        .options(selectinload(Account.roles))
        .where(Account.account_id == request.account_id)
    )).scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Kiểm tra không phải admin
    roles = [role.title for role in account.roles]
    if "ADMIN" in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot ban admin account"
        )
    
    if account.status == "BANNED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already banned"
        )
    
    account.status = "BANNED"
    await db.commit()
    await db.refresh(account)
    
    return BanAccountResponse(
        message="Account has been banned successfully",
        account_id=account.account_id,
        status=account.status
    )


@router.post("/unban", response_model=BanAccountResponse)
async def unban_account(
    request: BanAccountRequest,
    current_admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Bỏ cấm tài khoản khách hàng hoặc đối tác"""
    account = (await db.execute(
        select(Account).where(Account.account_id == request.account_id)
    )).scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if account.status != "BANNED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is not banned"
        )
    
    account.status = "ACTIVE"
    await db.commit()
    await db.refresh(account)
    
    return BanAccountResponse(
        message="Account has been unbanned successfully",
        account_id=account.account_id,
        status=account.status
    )


@router.get("/{account_id}")
async def get_account_detail(
    account_id: int,
    current_admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Xem chi tiết tài khoản"""
    # Eager load relationships để tránh lỗi lazy loading trong async
    account = (await db.execute(
        select(Account)
        .options(
            selectinload(Account.roles),
            selectinload(Account.customer),
            selectinload(Account.partner)
        )
        .where(Account.account_id == account_id)
    )).scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    response = {
        "account_id": account.account_id,
        "username": account.username,
        "status": account.status,
        "created_at": account.created_at,
        "roles": [role.title for role in account.roles]
    }
    
    # Thêm thông tin customer nếu có
    if account.customer:
        response["customer"] = {
            "id": account.customer.id,
            "fullname": account.customer.fullname,
            "email": account.customer.email,
            "phone_number": account.customer.phone_number,
            "id_number": account.customer.id_number
        }
    
    # Thêm thông tin partner nếu có
    if account.partner:
        response["partner"] = {
            "id": account.partner.id,
            "name": account.partner.name,
            "phone_number": account.partner.phone_number,
            "address": account.partner.address,
            "banking_number": account.partner.banking_number,
            "bank": account.partner.bank,
            "balance": float(account.partner.balance) if account.partner.balance else 0
        }
    
    return response

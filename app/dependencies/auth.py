from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.db_async import get_db as get_db_async
from app.models.account import Account
from app.models.partner import Partner
from app.services.auth_service import validate_token, get_account_roles

security = HTTPBearer()


def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Account:
    """Dependency để xác thực user và trả về account"""
    token = credentials.credentials
    account = validate_token(db, token)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return account


def require_role(required_roles: list[str]):
    """
    Factory function tạo dependency kiểm tra role.
    
    Usage:
        @router.get("/admin/dashboard")
        def admin_dashboard(account: Account = Depends(require_role(["ADMIN"]))):
            ...
    """
    def role_checker(account: Account = Depends(get_current_account)) -> Account:
        user_roles = get_account_roles(account)
        
        # Kiểm tra xem user có ít nhất 1 role trong required_roles không
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bạn không có quyền truy cập. Yêu cầu role: {', '.join(required_roles)}"
            )
        
        return account
    
    return role_checker


def get_current_admin(account: Account = Depends(get_current_account)) -> Account:
    """Dependency yêu cầu role ADMIN"""
    user_roles = get_account_roles(account)
    
    if "ADMIN" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ACCESS_DENIED"
        )
    
    return account


def get_current_partner(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Partner:
    """Dependency yêu cầu role PARTNER"""
    token = credentials.credentials
    account = validate_token(db, token)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED"
        )
    
    user_roles = get_account_roles(account)
    
    if "PARTNER" not in user_roles or not account.partner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ACCESS_DENIED"
        )
    
    return account.partner


def get_current_customer(account: Account = Depends(get_current_account)):
    """Dependency yêu cầu role CUSTOMER"""
    user_roles = get_account_roles(account)
    
    if "CUSTOMER" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Customer mới có quyền truy cập"
        )
    
    if not account.customer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không có thông tin khách hàng"
        )
    
    return account.customer



# ==================== ASYNC VERSIONS ====================

async def get_current_account_async(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_async)
) -> Account:
    """Async dependency để xác thực user và trả về account"""
    from app.models.account_token import AccountToken
    from app.services.auth_service import decode_token
    from datetime import datetime
    
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    account_id = payload.get("sub")
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ"
        )
    
    # Kiểm tra token trong database
    token_result = await db.execute(
        select(AccountToken).where(
            AccountToken.token_value == token,
            AccountToken.is_revoked == False,
            AccountToken.expires_at > datetime.utcnow()
        )
    )
    account_token = token_result.scalar_one_or_none()
    
    if not account_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn"
        )
    
    # Lấy account với eager loading
    result = await db.execute(
        select(Account)
        .options(selectinload(Account.roles))
        .where(Account.account_id == int(account_id), Account.is_deleted == False)
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại"
        )
    
    return account


async def get_current_partner_async(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_async)
) -> Partner:
    """Async dependency yêu cầu role PARTNER - trả về Partner từ cùng session"""
    from app.models.account_token import AccountToken
    from app.services.auth_service import decode_token
    from datetime import datetime
    
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED"
        )
    
    account_id = payload.get("sub")
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED"
        )
    
    # Kiểm tra token
    token_result = await db.execute(
        select(AccountToken).where(
            AccountToken.token_value == token,
            AccountToken.is_revoked == False,
            AccountToken.expires_at > datetime.utcnow()
        )
    )
    if not token_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED"
        )
    
    # Lấy account với roles và partner
    result = await db.execute(
        select(Account)
        .options(
            selectinload(Account.roles),
            selectinload(Account.partner)
        )
        .where(Account.account_id == int(account_id), Account.is_deleted == False)
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED"
        )
    
    user_roles = [role.title for role in account.roles]
    
    if "PARTNER" not in user_roles or not account.partner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ACCESS_DENIED"
        )
    
    return account.partner

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest, RegisterResponse, 
    LoginRequest, TokenResponse,
    LogoutResponse, AccountResponse,
    PartnerRegisterRequest, PartnerRegisterResponse, PartnerResponse
)
from app.services.auth_service import (
    get_account_by_username, register_account,
    login_account, logout_account, validate_token,
    get_account_roles, register_partner_account, LoginError
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Đăng ký tài khoản mới"""
    # Kiểm tra username đã tồn tại
    existing_account = get_account_by_username(db, request.username)
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    try:
        account = register_account(db, request.username, request.password)
        return RegisterResponse(
            message="Registration successful",
            account=AccountResponse(
                account_id=account.account_id,
                username=account.username,
                status=account.status,
                created_at=account.created_at,
                roles=get_account_roles(account)
            )
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Đăng nhập"""
    result = login_account(db, request.username, request.password)
    
    # Kiểm tra nếu là lỗi
    if isinstance(result, LoginError):
        if result.error_type == "pending":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.message
            )
        elif result.error_type == "rejected":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.message
            )
        elif result.error_type == "banned":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.message,
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    account, access_token, expires_at = result
    return TokenResponse(
        access_token=access_token,
        expires_at=expires_at
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Đăng xuất - revoke token hiện tại"""
    token = credentials.credentials
    
    success = logout_account(db, token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already revoked token"
        )
    
    return LogoutResponse(message="Logout successful")


@router.get("/me")
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Lấy thông tin user hiện tại"""
    token = credentials.credentials
    account = validate_token(db, token)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    roles = get_account_roles(account)
    
    response = {
        "account_id": account.account_id,
        "username": account.username,
        "status": account.status,
        "created_at": account.created_at,
        "roles": roles
    }
    
    # Thêm thông tin customer đầy đủ nếu là CUSTOMER
    if "CUSTOMER" in roles and account.customer:
        response["customer"] = {
            "id": account.customer.id,
            "fullname": account.customer.fullname,
            "email": account.customer.email,
            "phone_number": account.customer.phone_number,
            "id_number": account.customer.id_number
        }
    
    # Thêm thông tin partner đầy đủ nếu là PARTNER
    if "PARTNER" in roles and account.partner:
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


# Dependency để sử dụng trong các router khác
def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependency để xác thực user trong các endpoint khác"""
    token = credentials.credentials
    account = validate_token(db, token)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return account



@router.post("/register/partner", response_model=PartnerRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_partner(request: PartnerRegisterRequest, db: Session = Depends(get_db)):
    """Đăng ký tài khoản đối tác - cần admin duyệt mới được hoạt động"""
    # Kiểm tra username đã tồn tại
    existing_account = get_account_by_username(db, request.username)
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    try:
        account, partner = register_partner_account(
            db=db,
            username=request.username,
            password=request.password,
            name=request.name,
            phone_number=request.phone_number,
            address=request.address,
            banking_number=request.banking_number,
            bank=request.bank
        )
        
        return PartnerRegisterResponse(
            message="Partner registration submitted. Please wait for admin approval.",
            partner=PartnerResponse(
                id=partner.id,
                account_id=partner.account_id,
                name=partner.name,
                phone_number=partner.phone_number,
                address=partner.address,
                banking_number=partner.banking_number,
                bank=partner.bank,
                account_status=account.status
            )
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


from app.schemas.auth import UpdateCustomerRequest, UpdatePartnerRequest, ChangePasswordRequest
from app.services.auth_service import verify_password, hash_password


@router.put("/me/customer")
def update_customer_profile(
    request: UpdateCustomerRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin customer"""
    token = credentials.credentials
    account = validate_token(db, token)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    if not account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản không phải là customer"
        )
    
    customer = account.customer
    
    # Cập nhật các field nếu có
    if request.fullname is not None:
        customer.fullname = request.fullname
    if request.email is not None:
        customer.email = request.email
    if request.phone_number is not None:
        customer.phone_number = request.phone_number
    if request.id_number is not None:
        customer.id_number = request.id_number
    
    db.commit()
    db.refresh(customer)
    
    return {
        "message": "Cập nhật thông tin thành công",
        "customer": {
            "id": customer.id,
            "fullname": customer.fullname,
            "email": customer.email,
            "phone_number": customer.phone_number,
            "id_number": customer.id_number
        }
    }


@router.put("/me/partner")
def update_partner_profile(
    request: UpdatePartnerRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin partner"""
    token = credentials.credentials
    account = validate_token(db, token)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    if not account.partner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản không phải là partner"
        )
    
    partner = account.partner
    
    # Cập nhật các field nếu có
    if request.name is not None:
        partner.name = request.name
    if request.phone_number is not None:
        partner.phone_number = request.phone_number
    if request.address is not None:
        partner.address = request.address
    if request.banking_number is not None:
        partner.banking_number = request.banking_number
    if request.bank is not None:
        partner.bank = request.bank
    
    db.commit()
    db.refresh(partner)
    
    return {
        "message": "Cập nhật thông tin thành công",
        "partner": {
            "id": partner.id,
            "name": partner.name,
            "phone_number": partner.phone_number,
            "address": partner.address,
            "banking_number": partner.banking_number,
            "bank": partner.bank
        }
    }


@router.put("/me/password")
def change_password(
    request: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Đổi mật khẩu"""
    token = credentials.credentials
    account = validate_token(db, token)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Kiểm tra mật khẩu cũ
    if not verify_password(request.old_password, account.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu cũ không đúng"
        )
    
    # Cập nhật mật khẩu mới
    account.password = hash_password(request.new_password)
    db.commit()
    
    return {"message": "Đổi mật khẩu thành công"}

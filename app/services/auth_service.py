from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
import os

from app.models.account import Account
from app.models.account_token import AccountToken
from app.models.account_assign_role import AccountAssignRole
from app.models.role import Role

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> tuple[str, datetime]:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_account_by_username(db: Session, username: str) -> Optional[Account]:
    return db.query(Account).filter(
        Account.username == username,
        Account.is_deleted == False
    ).first()


def get_account_by_id(db: Session, account_id: int) -> Optional[Account]:
    return db.query(Account).filter(
        Account.account_id == account_id,
        Account.is_deleted == False
    ).first()


def register_account(
    db: Session, 
    username: str, 
    password: str, 
    role_title: str = "CUSTOMER",
    fullname: str = None,
    email: str = None,
    phone_number: str = None,
    id_number: str = None
) -> Account:
    """Đăng ký tài khoản mới"""
    from app.models.customer import Customer
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Tạo account
    new_account = Account(
        username=username,
        password=hashed_password,
        status="ACTIVE",
        is_deleted=False
    )
    db.add(new_account)
    db.flush()  # Để lấy account_id
    
    # Gán role mặc định
    role = db.query(Role).filter(Role.title == role_title).first()
    if role:
        account_role = AccountAssignRole(
            account_id=new_account.account_id,
            role_id=role.id
        )
        db.add(account_role)
    
    # Tạo Customer profile nếu role là CUSTOMER
    if role_title == "CUSTOMER":
        new_customer = Customer(
            account_id=new_account.account_id,
            fullname=fullname,
            email=email,
            phone_number=phone_number,
            id_number=id_number,
            is_deleted=False
        )
        db.add(new_customer)
    
    db.commit()
    db.refresh(new_account)
    return new_account


class LoginError:
    """Class để phân biệt các loại lỗi login"""
    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message


def login_account(db: Session, username: str, password: str) -> tuple[Account, str, datetime] | LoginError:
    """Đăng nhập và tạo token"""
    account = get_account_by_username(db, username)
    
    if not account:
        return LoginError("invalid_credentials", "Invalid username or password")
    
    if not verify_password(password, account.password):
        return LoginError("invalid_credentials", "Invalid username or password")
    
    if account.status == "PENDING":
        return LoginError("pending", "Account is pending approval. Please wait for admin to approve.")
    
    if account.status == "REJECTED":
        return LoginError("rejected", "Account registration was rejected.")
    
    if account.status == "BANNED":
        return LoginError("banned", "Account has been banned. Please contact support.")
    
    if account.status != "ACTIVE":
        return LoginError("inactive", "Account is not active.")
    
    # Tạo access token
    token_data = {
        "sub": str(account.account_id),
        "username": account.username
    }
    access_token, expires_at = create_access_token(token_data)
    
    # Lưu token vào database
    account_token = AccountToken(
        account_id=account.account_id,
        token_value=access_token,
        expires_at=expires_at,
        is_revoked=False
    )
    db.add(account_token)
    db.commit()
    
    return account, access_token, expires_at


def logout_account(db: Session, token: str) -> bool:
    """Đăng xuất - revoke token"""
    account_token = db.query(AccountToken).filter(
        AccountToken.token_value == token,
        AccountToken.is_revoked == False
    ).first()
    
    if not account_token:
        return False
    
    account_token.is_revoked = True
    db.commit()
    return True


def validate_token(db: Session, token: str) -> Optional[Account]:
    """Kiểm tra token hợp lệ và trả về account"""
    # Decode token
    payload = decode_token(token)
    if not payload:
        return None
    
    account_id = payload.get("sub")
    if not account_id:
        return None
    
    # Kiểm tra token trong database
    account_token = db.query(AccountToken).filter(
        AccountToken.token_value == token,
        AccountToken.is_revoked == False,
        AccountToken.expires_at > datetime.utcnow()
    ).first()
    
    if not account_token:
        return None
    
    return get_account_by_id(db, int(account_id))


def get_account_roles(account: Account) -> list[str]:
    """Lấy danh sách role của account"""
    return [role.title for role in account.roles]


from app.models.partner import Partner


def register_partner_account(
    db: Session, 
    username: str, 
    password: str,
    name: str,
    phone_number: str,
    address: str,
    banking_number: str,
    bank: str
) -> tuple[Account, Partner]:
    """Đăng ký tài khoản đối tác - trạng thái PENDING chờ admin duyệt"""
    hashed_password = hash_password(password)
    
    # Tạo account với status PENDING
    new_account = Account(
        username=username,
        password=hashed_password,
        status="PENDING",  # Chờ admin duyệt
        is_deleted=False
    )
    db.add(new_account)
    db.flush()
    
    # Gán role PARTNER
    role = db.query(Role).filter(Role.title == "PARTNER").first()
    if role:
        account_role = AccountAssignRole(
            account_id=new_account.account_id,
            role_id=role.id
        )
        db.add(account_role)
    
    # Tạo partner profile
    new_partner = Partner(
        account_id=new_account.account_id,
        name=name,
        phone_number=phone_number,
        address=address,
        banking_number=banking_number,
        bank=bank,
        balance=0
    )
    db.add(new_partner)
    
    db.commit()
    db.refresh(new_account)
    db.refresh(new_partner)
    
    return new_account, new_partner


def get_pending_partners(db: Session) -> list:
    """Lấy danh sách đối tác đang chờ duyệt"""
    return db.query(Partner, Account).join(
        Account, Partner.account_id == Account.account_id
    ).filter(
        Account.status == "PENDING",
        Account.is_deleted == False
    ).all()


def approve_partner(db: Session, account_id: int, approved: bool) -> Optional[Account]:
    """Admin duyệt hoặc từ chối đối tác"""
    account = db.query(Account).filter(
        Account.account_id == account_id,
        Account.status == "PENDING",
        Account.is_deleted == False
    ).first()
    
    if not account:
        return None
    
    if approved:
        account.status = "ACTIVE"
    else:
        account.status = "REJECTED"
    
    db.commit()
    db.refresh(account)
    return account

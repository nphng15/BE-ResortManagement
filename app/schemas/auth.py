from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)
    fullname: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=150)
    phone_number: Optional[str] = Field(None, max_length=10)
    id_number: Optional[str] = Field(None, max_length=15)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class AccountResponse(BaseModel):
    account_id: int
    username: str
    status: str
    created_at: datetime
    roles: List[str] = []

    class Config:
        from_attributes = True


class RegisterResponse(BaseModel):
    message: str
    account: AccountResponse


class LogoutResponse(BaseModel):
    message: str


# Partner Registration
class PartnerRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)
    name: str = Field(..., max_length=100)
    phone_number: str = Field(..., max_length=10)
    address: str = Field(..., max_length=255)
    banking_number: str = Field(..., max_length=20)
    bank: str = Field(..., max_length=255)


class PartnerResponse(BaseModel):
    id: int
    account_id: int
    name: str
    phone_number: str
    address: str
    banking_number: str
    bank: str
    account_status: str

    class Config:
        from_attributes = True


class PartnerRegisterResponse(BaseModel):
    message: str
    partner: PartnerResponse


class PartnerApprovalRequest(BaseModel):
    account_id: int
    approved: bool  # True = duyệt, False = từ chối


class PartnerApprovalResponse(BaseModel):
    message: str
    account_id: int
    status: str


# Update Profile
class UpdateCustomerRequest(BaseModel):
    fullname: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=150)
    phone_number: Optional[str] = Field(None, max_length=10)
    id_number: Optional[str] = Field(None, max_length=15)


class UpdatePartnerRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = Field(None, max_length=255)
    banking_number: Optional[str] = Field(None, max_length=20)
    bank: Optional[str] = Field(None, max_length=255)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=255)

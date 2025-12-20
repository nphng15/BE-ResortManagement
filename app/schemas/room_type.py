from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal


class RoomTypeBase(BaseModel):
    name: str
    area: Optional[float] = None
    quantity_standard: Optional[str] = None
    quality_standard: Optional[str] = None
    bed_amount: Optional[int] = None
    people_amount: Optional[int] = None
    price: Optional[Decimal] = None


class OfferInRoomType(BaseModel):
    """Gói đặt phòng khi tạo loại phòng"""
    cost: Decimal


class RoomTypeCreate(RoomTypeBase):
    resort_id: int
    image_urls: List[str] = []
    offer: OfferInRoomType


class RoomTypeUpdate(BaseModel):
    name: Optional[str] = None
    area: Optional[float] = None
    quantity_standard: Optional[str] = None
    quality_standard: Optional[str] = None
    bed_amount: Optional[int] = None
    people_amount: Optional[int] = None
    price: Optional[Decimal] = None


class RoomImageOut(BaseModel):
    id: int
    url: str

    class Config:
        from_attributes = True


class ServiceOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class OfferOut(BaseModel):
    id: int
    room_type_id: int
    cost: Decimal

    class Config:
        from_attributes = True


class RoomTypeOut(RoomTypeBase):
    id: int
    resort_id: int
    images: List[RoomImageOut] = []
    offers: List[OfferOut] = []

    class Config:
        from_attributes = True


class OfferCreate(BaseModel):
    room_type_id: int
    cost: Decimal


class OfferUpdate(BaseModel):
    cost: Optional[Decimal] = None


class OfferWithDetails(OfferOut):
    room_type_name: Optional[str] = None
    resort_name: Optional[str] = None
    services: List[ServiceOut] = []

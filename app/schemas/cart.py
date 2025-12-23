from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CartItemResponse(BaseModel):
    id: int
    offer_id: int
    room_type_name: Optional[str] = None
    resort_name: Optional[str] = None
    number_of_rooms: int
    price_per_room: float
    cost: float
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    status: Optional[str] = None
    available_rooms: Optional[int] = None

    class Config:
        orm_mode = True


class CartResponse(BaseModel):
    id: int
    customer_id: int
    created_at: Optional[datetime] = None
    status: str
    total_cost: float
    items: List[CartItemResponse]

    class Config:
        orm_mode = True


class AddToCartRequest(BaseModel):
    """Request body để thêm item vào giỏ - không cần customer_id vì lấy từ token"""
    offer_id: int
    number_of_rooms: int
    started_at: datetime
    finished_at: datetime

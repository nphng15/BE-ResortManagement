from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from typing import List
from decimal import Decimal

from app.models.account import Account
from app.models.booking import Booking
from app.models.booking_detail import BookingDetail
from app.models.invoice import Invoice
from app.models.number_of_room import BookingDetailUpdate
from app.models.offer import Offer
from app.models.room_type import RoomType
from app.models.resort import Resort
from app.schemas.booking import BookingDetailCreate
from app.schemas.cart import CartResponse, CartItemResponse, AddToCartRequest
from app.db_async import get_db
from app.schemas.payment import PaymentRequest
from app.services import crud_booking as crud
from app.dependencies.auth import get_current_account

router = APIRouter(prefix="/api/v1", tags=["Cart"])


@router.get("/cart", response_model=CartResponse)
async def get_cart(
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy giỏ hàng của khách hàng hiện tại (booking có status = 'pending')
    """
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    result = await db.execute(
        select(Booking)
        .filter(Booking.customer_id == customer_id, Booking.status == "pending")
        .options(
            selectinload(Booking.booking_details)
            .selectinload(BookingDetail.offer)
            .selectinload(Offer.room_type)
            .selectinload(RoomType.resort)
        )
        .order_by(Booking.created_at.desc())
    )
    cart = result.scalar_one_or_none()

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy giỏ hàng"
        )

    cart_items: List[CartItemResponse] = []
    total_cost = Decimal("0")

    for detail in cart.booking_details:
        offer = detail.offer
        room_type = offer.room_type if offer else None
        resort = room_type.resort if room_type else None

        item = CartItemResponse(
            id=detail.id,
            offer_id=detail.offer_id,
            room_type_name=room_type.name if room_type else None,
            resort_name=resort.name if resort else None,
            number_of_rooms=detail.number_of_rooms,
            price_per_room=float(offer.cost) if offer and offer.cost else 0,
            cost=float(detail.cost) if detail.cost else 0,
            started_at=detail.started_at,
            finished_at=detail.finished_at,
            status=detail.status
        )
        cart_items.append(item)
        total_cost += detail.cost if detail.cost else Decimal("0")

    return CartResponse(
        id=cart.id,
        customer_id=cart.customer_id,
        created_at=cart.created_at,
        status=cart.status,
        total_cost=float(total_cost),
        items=cart_items
    )


@router.post("/cart/items", status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    request: AddToCartRequest,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db)
):
    """
    Thêm item vào giỏ hàng
    """
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    cart = await crud.get_or_create_cart(db=db, customer_id=customer_id)

    booking_detail = BookingDetailCreate(
        offer_id=request.offer_id,
        number_of_rooms=request.number_of_rooms,
        started_at=request.started_at,
        finished_at=request.finished_at,
        status="pending",
        customer_id=customer_id
    )

    await crud.add_booking_detail(db=db, booking_id=cart.id, booking_detail=booking_detail)

    return {"message": "Item added to cart successfully"}


@router.put("/booking-detail/{booking_detail_id}")
async def update_booking_detail(
    booking_detail_id: int, 
    booking_detail_update: BookingDetailUpdate,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db)
):
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    result = await db.execute(
        select(BookingDetail)
        .filter(BookingDetail.id == booking_detail_id)
        .options(selectinload(BookingDetail.booking))
    )
    booking_detail = result.scalar_one_or_none()
    
    if not booking_detail:
        raise HTTPException(status_code=404, detail="Booking Detail not found")
    
    if booking_detail.booking.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền chỉnh sửa item này"
        )
    
    if booking_detail.booking.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Không thể chỉnh sửa item từ đơn hàng đã thanh toán"
        )
    
    offer_result = await db.execute(select(Offer).filter(Offer.id == booking_detail.offer_id))
    offer = offer_result.scalar_one_or_none()
    offer_price = offer.cost if offer and offer.cost else Decimal("0")

    old_cost = booking_detail.cost or Decimal("0")

    booking_detail.number_of_rooms = booking_detail_update.number_of_rooms
    booking_detail.cost = booking_detail.number_of_rooms * offer_price

    booking = booking_detail.booking
    if booking.cost is None:
        booking.cost = Decimal("0")
    booking.cost = booking.cost - old_cost + booking_detail.cost
    
    await db.commit()
    await db.refresh(booking_detail)

    return {"message": "Booking Detail updated successfully", "booking_detail": booking_detail}


@router.delete("/booking-detail/{booking_detail_id}")
async def delete_booking_detail(
    booking_detail_id: int,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db)
):
    """
    Xóa một item khỏi giỏ hàng
    """
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    result = await db.execute(
        select(BookingDetail)
        .filter(BookingDetail.id == booking_detail_id)
        .options(selectinload(BookingDetail.booking))
    )
    booking_detail = result.scalar_one_or_none()

    if not booking_detail:
        raise HTTPException(status_code=404, detail="Booking Detail not found")

    if booking_detail.booking.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa item này"
        )

    if booking_detail.booking.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Không thể xóa item từ đơn hàng đã thanh toán"
        )

    item_cost = booking_detail.cost or Decimal("0")
    booking = booking_detail.booking

    await db.delete(booking_detail)

    if booking.cost:
        booking.cost = booking.cost - item_cost
    
    await db.commit()

    return {"message": "Item đã được xóa khỏi giỏ hàng"}


@router.post("/booking-detail/{booking_detail_id}/cancel")
async def cancel_booking_detail(
    booking_detail_id: int,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db)
):
    """
    Hủy một booking detail đã thanh toán
    """
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    result = await db.execute(
        select(BookingDetail)
        .filter(BookingDetail.id == booking_detail_id)
        .options(selectinload(BookingDetail.booking))
    )
    booking_detail = result.scalar_one_or_none()

    if not booking_detail:
        raise HTTPException(status_code=404, detail="Booking Detail not found")

    if booking_detail.booking.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền hủy booking này"
        )

    if booking_detail.status != "PAID":
        raise HTTPException(
            status_code=400,
            detail="Chỉ có thể hủy booking đã thanh toán"
        )

    booking_detail.status = "CANCELLED"
    await db.commit()
    await db.refresh(booking_detail)

    return {"message": "Booking đã được hủy thành công", "booking_detail_id": booking_detail_id}


@router.post("/payment")
async def process_payment(
    payment_request: PaymentRequest, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(BookingDetail)
        .filter(BookingDetail.id == payment_request.booking_detail_id)
        .options(
            selectinload(BookingDetail.booking),
            selectinload(BookingDetail.offer)
            .selectinload(Offer.room_type)
            .selectinload(RoomType.resort)
        )
    )
    booking_detail = result.scalar_one_or_none()

    if not booking_detail:
        raise HTTPException(status_code=404, detail="Booking Detail not found")

    if payment_request.payment_status != "success":
        raise HTTPException(status_code=400, detail="Payment not successful")

    booking_detail.status = "PAID"
    db.add(booking_detail)
    await db.commit()
    await db.refresh(booking_detail)

    # Lấy partner_id từ resort
    partner_id = booking_detail.offer.room_type.resort.partner_id

    invoice = Invoice(
        customer_id=booking_detail.booking.customer_id,
        partner_id=partner_id,
        booking_detail_id=booking_detail.id,
        cost=payment_request.paid_amount,
        payment_method=payment_request.payment_method,
    )
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)

    return invoice

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.orm import Session
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
from app.database import get_db
from app.schemas.payment import PaymentRequest
from app.services import crud_booking as crud
from app.dependencies.auth import get_current_account

router = APIRouter(prefix="/api/v1", tags=["Cart"])


@router.get("/cart", response_model=CartResponse)
def get_cart(
    current_account: Account = Depends(get_current_account),
    db: Session = Depends(get_db)
):
    """
    Lấy giỏ hàng của khách hàng hiện tại (booking có status = 'pending')
    """
    # Lấy customer_id từ account
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    # Query booking với eager loading các relationships
    result = db.execute(
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

    # Build response
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
def add_to_cart(
    request: AddToCartRequest,
    current_account: Account = Depends(get_current_account),
    db: Session = Depends(get_db)
):
    """
    Thêm item vào giỏ hàng
    """
    # Lấy customer_id từ token
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    # Lấy hoặc tạo giỏ hàng mới nếu chưa có
    cart = crud.get_or_create_cart(db=db, customer_id=customer_id)

    # Tạo booking detail từ request
    booking_detail = BookingDetailCreate(
        offer_id=request.offer_id,
        number_of_rooms=request.number_of_rooms,
        started_at=request.started_at,
        finished_at=request.finished_at,
        status="pending",
        customer_id=customer_id
    )

    # Thêm BookingDetail vào giỏ
    crud.add_booking_detail(db=db, booking_id=cart.id, booking_detail=booking_detail)

    return {"message": "Item added to cart successfully"}

@router.put("/booking-detail/{booking_detail_id}")
def update_booking_detail(
    booking_detail_id: int, 
    booking_detail_update: BookingDetailUpdate,
    current_account: Account = Depends(get_current_account),
    db: Session = Depends(get_db)
):
    # Kiểm tra customer
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    # Tìm booking_detail kèm booking để kiểm tra ownership
    result = db.execute(
        select(BookingDetail)
        .filter(BookingDetail.id == booking_detail_id)
        .options(selectinload(BookingDetail.booking))
    )
    booking_detail = result.scalar_one_or_none()
    
    if not booking_detail:
        raise HTTPException(status_code=404, detail="Booking Detail not found")
    
    # Kiểm tra ownership - item này có thuộc về user hiện tại không
    if booking_detail.booking.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền chỉnh sửa item này"
        )
    
    # Kiểm tra booking có đang pending không
    if booking_detail.booking.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Không thể chỉnh sửa item từ đơn hàng đã thanh toán"
        )
    
    # Lấy giá từ Offer
    offer_result = db.execute(select(Offer).filter(Offer.id == booking_detail.offer_id))
    offer = offer_result.scalar_one_or_none()
    offer_price = offer.cost if offer and offer.cost else Decimal("0")

    # Lưu cost cũ để cập nhật booking
    old_cost = booking_detail.cost or Decimal("0")

    # Cập nhật số lượng phòng và tính lại cost
    booking_detail.number_of_rooms = booking_detail_update.number_of_rooms
    booking_detail.cost = booking_detail.number_of_rooms * offer_price

    # Cập nhật tổng cost của booking
    booking = booking_detail.booking
    if booking.cost is None:
        booking.cost = Decimal("0")
    booking.cost = booking.cost - old_cost + booking_detail.cost
    
    db.commit()
    db.refresh(booking_detail)

    return {"message": "Booking Detail updated successfully", "booking_detail": booking_detail}


@router.delete("/booking-detail/{booking_detail_id}")
def delete_booking_detail(
    booking_detail_id: int,
    current_account: Account = Depends(get_current_account),
    db: Session = Depends(get_db)
):
    """
    Xóa một item khỏi giỏ hàng
    """
    # Kiểm tra customer
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    # Tìm booking_detail kèm booking
    result = db.execute(
        select(BookingDetail)
        .filter(BookingDetail.id == booking_detail_id)
        .options(selectinload(BookingDetail.booking))
    )
    booking_detail = result.scalar_one_or_none()

    if not booking_detail:
        raise HTTPException(status_code=404, detail="Booking Detail not found")

    # Kiểm tra ownership - item này có thuộc về user hiện tại không
    if booking_detail.booking.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa item này"
        )

    # Kiểm tra booking có đang pending không
    if booking_detail.booking.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Không thể xóa item từ đơn hàng đã thanh toán"
        )

    # Lưu cost để trừ khỏi booking
    item_cost = booking_detail.cost or Decimal("0")
    booking = booking_detail.booking

    # Xóa booking_detail
    db.delete(booking_detail)

    # Cập nhật tổng cost của booking
    if booking.cost:
        booking.cost = booking.cost - item_cost
    
    db.commit()

    return {"message": "Item đã được xóa khỏi giỏ hàng"}

@router.post("/booking-detail/{booking_detail_id}/cancel")
def cancel_booking_detail(
    booking_detail_id: int,
    current_account: Account = Depends(get_current_account),
    db: Session = Depends(get_db)
):
    """
    Hủy một booking detail đã thanh toán
    """
    # Kiểm tra customer
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    # Tìm booking_detail kèm booking
    result = db.execute(
        select(BookingDetail)
        .filter(BookingDetail.id == booking_detail_id)
        .options(selectinload(BookingDetail.booking))
    )
    booking_detail = result.scalar_one_or_none()

    if not booking_detail:
        raise HTTPException(status_code=404, detail="Booking Detail not found")

    # Kiểm tra ownership
    if booking_detail.booking.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền hủy booking này"
        )

    # Chỉ cho phép hủy booking đã thanh toán (PAID)
    if booking_detail.status != "PAID":
        raise HTTPException(
            status_code=400,
            detail="Chỉ có thể hủy booking đã thanh toán"
        )

    # Cập nhật trạng thái thành CANCELLED
    booking_detail.status = "CANCELLED"
    db.commit()
    db.refresh(booking_detail)

    return {"message": "Booking đã được hủy thành công", "booking_detail_id": booking_detail_id}


@router.post("/payment")
def process_payment(
    payment_request: PaymentRequest, 
    db: AsyncSession = Depends(get_db)
):
    # Tìm BookingDetail theo booking_detail_id trong một ngữ cảnh bất đồng bộ đúng
    result = db.execute(select(BookingDetail).filter(BookingDetail.id == payment_request.booking_detail_id).options(selectinload(BookingDetail.booking)))
    booking_detail = result.scalar_one_or_none()

    if not booking_detail:
        raise HTTPException(status_code=404, detail="Booking Detail not found")

    # Kiểm tra trạng thái thanh toán
    if payment_request.payment_status != "success":
        raise HTTPException(status_code=400, detail="Payment not successful")

    # Cập nhật trạng thái của booking_detail thành "PAID"
    booking_detail.status = "PAID"
    db.add(booking_detail)
    db.commit()  # Chắc chắn là await đúng
    db.refresh(booking_detail)  # Đảm bảo refresh sau khi commit

    # Tạo hóa đơn
    invoice = Invoice(
        customer_id=booking_detail.booking.customer_id,  # Giả sử bạn có mối quan hệ booking với customer
        partner_id=1,  # Partner ID có thể là một giá trị cố định hoặc từ hệ thống
        booking_detail_id=booking_detail.id,
        cost=payment_request.paid_amount,
        payment_method=payment_request.payment_method,
    )
    db.add(invoice)
    db.commit()  # Chắc chắn là await đúng
    db.refresh(invoice)  # Đảm bảo refresh sau khi commit

    # Trả về hóa đơn đã tạo
    return invoice

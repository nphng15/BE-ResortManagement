from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload, joinedload
from typing import List
from decimal import Decimal

from app.models.account import Account
from app.models.booking import Booking
from app.models.booking_detail import BookingDetail
from app.models.booking_timeslot import BookingTimeSlot
from app.models.invoice import Invoice
from app.models.number_of_room import BookingDetailUpdate
from app.models.offer import Offer
from app.models.room_type import RoomType
from app.models.room import Room
from app.models.resort import Resort
from app.schemas.booking import BookingDetailCreate
from app.schemas.cart import CartResponse, CartItemResponse, AddToCartRequest
from app.db_async import get_db
from app.schemas.payment import PaymentRequest
from app.services import crud_booking as crud
from app.services.booking_timeslot_service import create_booking_timeslots, validate_room_availability, delete_booking_timeslots_by_invoice
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

        # Calculate available rooms for this item's date range
        available_rooms = 0
        if room_type and detail.started_at and detail.finished_at:
            # Count total rooms for this room type
            total_rooms_result = await db.execute(
                select(func.count(Room.id)).where(Room.room_type_id == room_type.id)
            )
            total_rooms = total_rooms_result.scalar() or 0

            # Count booked rooms in the date range
            booked_rooms_subq = (
                select(BookingTimeSlot.room_id)
                .join(Room, Room.id == BookingTimeSlot.room_id)
                .where(
                    and_(
                        Room.room_type_id == room_type.id,
                        BookingTimeSlot.started_time < detail.finished_at,
                        BookingTimeSlot.finished_time > detail.started_at
                    )
                )
                .distinct()
            )
            booked_rooms_result = await db.execute(
                select(func.count()).select_from(booked_rooms_subq.subquery())
            )
            booked_rooms = booked_rooms_result.scalar() or 0

            available_rooms = total_rooms - booked_rooms

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
            status=detail.status,
            available_rooms=available_rooms
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
    Thêm item vào giỏ hàng.
    Nếu đã có item với cùng offer_id và cùng khoảng thời gian thì tăng number_of_rooms.
    """
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    cart = await crud.get_or_create_cart(db=db, customer_id=customer_id)

    # Check xem đã có item với cùng offer_id và cùng khoảng thời gian chưa
    existing_item_result = await db.execute(
        select(BookingDetail)
        .filter(
            BookingDetail.booking_id == cart.id,
            BookingDetail.offer_id == request.offer_id,
            BookingDetail.started_at == request.started_at,
            BookingDetail.finished_at == request.finished_at,
            BookingDetail.status == "pending"
        )
    )
    existing_item = existing_item_result.scalar_one_or_none()

    if existing_item:
        # Tăng số lượng phòng
        new_number_of_rooms = existing_item.number_of_rooms + request.number_of_rooms

        # Check phòng còn trống với số lượng mới
        await validate_room_availability(
            db=db,
            offer_id=request.offer_id,
            number_of_rooms=new_number_of_rooms,
            started_at=request.started_at,
            finished_at=request.finished_at
        )

        # Lấy giá offer
        offer_result = await db.execute(select(Offer).filter(Offer.id == request.offer_id))
        offer = offer_result.scalar_one_or_none()
        offer_price = offer.cost if offer and offer.cost else Decimal("0")

        old_cost = existing_item.cost or Decimal("0")
        existing_item.number_of_rooms = new_number_of_rooms
        existing_item.cost = new_number_of_rooms * offer_price

        # Cập nhật tổng cost của booking
        if cart.cost is None:
            cart.cost = Decimal("0")
        cart.cost = cart.cost - old_cost + existing_item.cost

        await db.commit()
        return {"message": "Đã tăng số lượng phòng trong giỏ hàng"}
    else:
        # Check phòng còn trống trước khi thêm vào giỏ
        await validate_room_availability(
            db=db,
            offer_id=request.offer_id,
            number_of_rooms=request.number_of_rooms,
            started_at=request.started_at,
            finished_at=request.finished_at
        )

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
    
    # Check phòng còn trống nếu tăng số lượng phòng
    if booking_detail_update.number_of_rooms > booking_detail.number_of_rooms:
        await validate_room_availability(
            db=db,
            offer_id=booking_detail.offer_id,
            number_of_rooms=booking_detail_update.number_of_rooms,
            started_at=booking_detail.started_at,
            finished_at=booking_detail.finished_at
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
    try:
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

        # So sánh status không phân biệt hoa thường
        if not booking_detail.status or booking_detail.status.upper() != "PAID":
            raise HTTPException(
                status_code=400,
                detail="Chỉ có thể hủy booking đã thanh toán"
            )

        # Lấy invoice đầu tiên để xóa BookingTimeSlot
        invoice_result = await db.execute(
            select(Invoice).filter(Invoice.booking_detail_id == booking_detail_id).limit(1)
        )
        invoice = invoice_result.scalar_one_or_none()

        if invoice:
            # Xóa BookingTimeSlot để giải phóng phòng
            await delete_booking_timeslots_by_invoice(db, invoice.id)

        booking_detail.status = "CANCELLED"
        await db.commit()

        return {"message": "Booking đã được hủy thành công", "booking_detail_id": booking_detail_id}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error cancelling booking: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi hủy booking: {str(e)}")


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
    await db.flush()
    
    # Tạo BookingTimeSlot cho các phòng được book
    await create_booking_timeslots(db, booking_detail, invoice_id=invoice.id)
    
    await db.commit()
    await db.refresh(invoice)

    return invoice

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select
from decimal import Decimal
from datetime import datetime
import json

from app.models.account import Account
from app.models.booking import Booking
from app.models.booking_detail import BookingDetail
from app.models.invoice import Invoice
from app.models.offer import Offer
from app.models.room_type import RoomType
from app.db_async import get_db
from app.schemas.zalopay import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    ZaloPayCallback,
    QueryPaymentRequest,
    QueryPaymentResponse
)
from app.services import zalopay_service
from app.dependencies.auth import get_current_account

router = APIRouter(prefix="/api/v1/zalopay", tags=["ZaloPay"])


@router.post("/create", response_model=CreatePaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo đơn thanh toán ZaloPay cho booking
    """
    if not current_account.customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có thông tin khách hàng"
        )
    customer_id = current_account.customer.id

    result = await db.execute(
        select(Booking).filter(
            Booking.id == request.booking_id,
            Booking.customer_id == customer_id,
            Booking.status == "pending"
        )
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking hoặc booking không thuộc về bạn"
        )

    amount = int(booking.cost or 0)
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Giỏ hàng trống hoặc chưa có giá"
        )

    zalo_result = zalopay_service.create_order(
        booking_id=booking.id,
        amount=amount,
        description=f"Thanh toan booking #{booking.id}",
        redirect_url=request.redirect_url or ""
    )

    if zalo_result.get("return_code") != 1:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ZaloPay error: {zalo_result.get('return_message')}"
        )

    booking.zp_trans_id = zalo_result.get("app_trans_id")
    await db.commit()

    return CreatePaymentResponse(
        return_code=zalo_result.get("return_code"),
        return_message=zalo_result.get("return_message"),
        order_url=zalo_result.get("order_url"),
        app_trans_id=zalo_result.get("app_trans_id"),
        zp_trans_token=zalo_result.get("zp_trans_token")
    )


@router.post("/callback")
async def zalopay_callback(callback: ZaloPayCallback, db: AsyncSession = Depends(get_db)):
    """
    Webhook nhận callback từ ZaloPay khi thanh toán hoàn tất
    """
    if not zalopay_service.verify_callback(callback.data, callback.mac):
        return {"return_code": -1, "return_message": "mac not equal"}

    try:
        data = json.loads(callback.data)
    except json.JSONDecodeError:
        return {"return_code": -1, "return_message": "invalid data"}

    app_trans_id = data.get("app_trans_id")
    embed_data = json.loads(data.get("embed_data", "{}"))
    booking_id = embed_data.get("booking_id")

    if not booking_id:
        return {"return_code": -1, "return_message": "missing booking_id"}

    result = await db.execute(
        select(Booking)
        .filter(Booking.id == booking_id)
        .options(
            selectinload(Booking.booking_details)
            .selectinload(BookingDetail.offer)
            .selectinload(Offer.room_type)
            .selectinload(RoomType.resort)
        )
    )
    booking = result.scalar_one_or_none()

    if booking and booking.status == "pending":
        booking.status = "paid"
        
        for detail in booking.booking_details:
            detail.status = "PAID"
            
            # Lấy partner_id từ resort
            partner_id = detail.offer.room_type.resort.partner_id
            
            invoice = Invoice(
                customer_id=booking.customer_id,
                partner_id=partner_id,
                booking_detail_id=detail.id,
                cost=detail.cost,
                finished_time=datetime.now(),
                payment_method="ZALOPAY"
            )
            db.add(invoice)
        
        await db.commit()

    return {"return_code": 1, "return_message": "success"}


@router.post("/query", response_model=QueryPaymentResponse)
async def query_payment(
    request: QueryPaymentRequest,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db)
):
    """
    Query trạng thái thanh toán từ ZaloPay
    """
    result = zalopay_service.query_order(request.app_trans_id)
    
    if result.get("return_code") == 1:
        booking_result = await db.execute(
            select(Booking)
            .filter(Booking.zp_trans_id == request.app_trans_id)
            .options(
                selectinload(Booking.booking_details)
                .selectinload(BookingDetail.offer)
                .selectinload(Offer.room_type)
                .selectinload(RoomType.resort)
            )
        )
        booking = booking_result.scalar_one_or_none()
        
        if booking and booking.status == "pending":
            booking.status = "paid"
            
            for detail in booking.booking_details:
                detail.status = "PAID"
                
                # Lấy partner_id từ resort
                partner_id = detail.offer.room_type.resort.partner_id
                
                invoice = Invoice(
                    customer_id=booking.customer_id,
                    partner_id=partner_id,
                    booking_detail_id=detail.id,
                    cost=detail.cost,
                    finished_time=datetime.now(),
                    payment_method="ZALOPAY"
                )
                db.add(invoice)
            
            await db.commit()

    return QueryPaymentResponse(
        return_code=result.get("return_code"),
        return_message=result.get("return_message"),
        is_processing=result.get("is_processing"),
        amount=result.get("amount"),
        zp_trans_id=result.get("zp_trans_id")
    )

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta
from typing import Optional

from app.db_async import get_db
from app.models.resort import Resort
from app.models.room_type import RoomType
from app.models.room import Room
from app.models.booking_timeslot import BookingTimeSlot
from app.models.resort_images import ResortImage
from app.models.service import Service

router = APIRouter(prefix="/api/v1", tags=["Search"])

@router.get("/search")
async def search_resorts(
    checkin: Optional[str] = Query(None),
    checkout: Optional[str] = Query(None),
    number: Optional[int] = Query(None),
    name: Optional[str] = Query(None, description="Search resort by name or address"),
    db: AsyncSession = Depends(get_db)
):
    print('here')
    if number is None:
        number = 1  # Mặc định là 1 người
    if checkin is None:
        checkin_date = datetime.now()
    else:
        try:
            # Kiểm tra nếu checkin là kiểu chuỗi hợp lệ trước khi chuyển đổi
            if isinstance(checkin, str):
                checkin_date = datetime.fromisoformat(checkin)
            else:
                raise ValueError("checkin should be a string")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for checkin, use YYYY-MM-DD")

    if checkout is None:
        checkout_date = checkin_date + timedelta(days=7)  # Mặc định là 7 ngày sau checkin
    else:
        try:
            # Kiểm tra nếu checkout là kiểu chuỗi hợp lệ trước khi chuyển đổi
            if isinstance(checkout, str):
                checkout_date = datetime.fromisoformat(checkout)
            else:
                raise ValueError("checkout should be a string")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for checkout, use YYYY-MM-DD")

    # 1️⃣ Subquery lấy các room bị trùng lịch
    subq = (
        select(BookingTimeSlot.room_id)
        .where(
            and_(
                BookingTimeSlot.started_time < checkout_date,
                BookingTimeSlot.finished_time > checkin_date
            )
        )
    )

    # 2️⃣ Resort có ít nhất 1 room trống
    stmt = (
        select(
            Resort.id,
            Resort.name,
            Resort.address,
            Resort.rating,
            func.min(RoomType.price).label("min_price")
        )
        .join(RoomType, RoomType.resort_id == Resort.id)
        .join(Room, Room.room_type_id == RoomType.id)
        .where(~Room.id.in_(subq) & (RoomType.people_amount >= number))
    )

    # 3️⃣ Filter theo name HOẶC address nếu có
    if name:
        stmt = stmt.where(
            or_(
                Resort.name.ilike(f"%{name}%"),
                Resort.address.ilike(f"%{name}%")
            )
        )

    stmt = stmt.group_by(Resort.id)

    result = await db.execute(stmt)
    resorts = result.all()

    # 4️⃣ Gắn thêm images và services
    output = []
    for r in resorts:
        # Lấy 4 ảnh đầu
        img_result = await db.execute(
            select(ResortImage.url)
            .where(ResortImage.resort_id == r.id)
            .limit(4)
        )
        images = [row[0] for row in img_result.all()]

        # Lấy danh sách dịch vụ
        sv_result = await db.execute(
            select(Service.name).where(Service.resort_id == r.id)
        )
        services = [row[0] for row in sv_result.all()]

        output.append({
            "id": r.id,
            "name": r.name,
            "address": r.address,
            "rating": r.rating,
            "min_price": float(r.min_price),
            "images": images,
            "services": services
        })

    return output
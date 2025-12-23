# API Quản lý Loại phòng & Gói đặt phòng cho Partner

## Xác thực
```
Authorization: Bearer <access_token>
```

---

## 1. Loại phòng (Room Type)

### `GET /api/v1/partner/resorts`
Lấy danh sách resort của partner.

### `GET /api/v1/partner/resorts/{resort_id}/services`
Lấy danh sách dịch vụ của resort (để chọn khi tạo gói).

### `GET /api/v1/partner/room-types?resort_id=`
Lấy tất cả loại phòng (có thể lọc theo resort).

### `POST /api/v1/partner/room-types`
Tạo loại phòng mới **kèm ảnh và 1 gói đặt phòng**.

```json
{
  "resort_id": 1,
  "name": "Deluxe Room",
  "area": 35.5,
  "bed_amount": 2,
  "people_amount": 4,
  "price": 2500000,
  "image_urls": ["https://example.com/img1.jpg"],
  "offer": {
    "name": "Gói cơ bản",
    "cost": 2000000,
    "service_ids": [1, 2]
  }
}
```

### `PUT /api/v1/partner/room-types/{id}`
Cập nhật loại phòng.

### `DELETE /api/v1/partner/room-types/{id}`
Xóa loại phòng.

---

## 2. Ảnh loại phòng

### `POST /api/v1/partner/room-types/{id}/images`
Thêm ảnh cho loại phòng.

### `DELETE /api/v1/partner/room-types/{id}/images/{image_id}`
Xóa ảnh.

---

## 3. Gói đặt phòng (Offer)

### `GET /api/v1/partner/offers`
Lấy tất cả gói đặt phòng của partner.

### `POST /api/v1/partner/offers`
Tạo thêm gói đặt phòng cho loại phòng đã có.

```json
{
  "room_type_id": 1,
  "name": "Gói VIP",
  "cost": 3500000,
  "service_ids": [1, 2, 3]
}
```

### `PUT /api/v1/partner/offers/{id}`
Cập nhật gói đặt phòng.

### `DELETE /api/v1/partner/offers/{id}`
Xóa gói đặt phòng.

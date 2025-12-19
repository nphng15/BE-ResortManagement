# API Lịch Sử Đặt Phòng

## Lấy lịch sử đặt phòng

Lấy danh sách lịch sử đặt phòng của khách hàng, bao gồm các booking đã thanh toán và đã hủy.

### Endpoint

```
GET /api/v1/customer/{id}/histories
```

### Parameters

| Tên | Vị trí | Kiểu | Bắt buộc | Mô tả |
|-----|--------|------|----------|-------|
| id | path | integer | Có | ID của khách hàng |

### Response

#### Success (200 OK)

Trả về danh sách lịch sử đặt phòng với thông tin chi tiết.

**Response Body:**

```json
[
  {
    "id": 1,
    "booking_id": 1,
    "cost": 2000000.0,
    "number_of_rooms": 1,
    "started_at": "2025-12-16T14:00:00",
    "finished_at": "2025-12-17T12:00:00",
    "status": "PAID",
    "room_type_name": "Deluxe Room",
    "room_type_id": 1,
    "resort_name": "Beach Resort",
    "resort_id": 1
  },
  {
    "id": 2,
    "booking_id": 2,
    "cost": 3000000.0,
    "number_of_rooms": 2,
    "started_at": "2025-12-20T14:00:00",
    "finished_at": "2025-12-22T12:00:00",
    "status": "CANCELLED",
    "room_type_name": "Suite Room",
    "room_type_id": 2,
    "resort_name": "Mountain Resort",
    "resort_id": 2
  }
]
```

**Response Fields:**

| Field | Kiểu | Mô tả |
|-------|------|-------|
| id | integer | ID của booking detail |
| booking_id | integer | ID của booking |
| cost | float | Tổng chi phí |
| number_of_rooms | integer | Số lượng phòng |
| started_at | datetime | Thời gian check-in |
| finished_at | datetime | Thời gian check-out |
| status | string | Trạng thái: `PAID` hoặc `CANCELLED` |
| room_type_name | string | Tên loại phòng |
| room_type_id | integer | ID loại phòng |
| resort_name | string | Tên resort |
| resort_id | integer | ID resort |

#### Error (404 Not Found)

Không tìm thấy lịch sử đặt phòng cho khách hàng này.

```json
{
  "detail": "No booking histories found for this customer"
}
```

### Trạng thái booking

API chỉ trả về các booking có trạng thái:

- **PAID**: Đã thanh toán thành công
- **CANCELLED**: Đã bị hủy bởi khách hàng

### Ví dụ

#### Request

```bash
curl -X GET "http://localhost:8000/api/v1/customer/1/histories"
```

#### Response

```json
[
  {
    "id": 4,
    "booking_id": 4,
    "cost": 2000000.0,
    "number_of_rooms": 1,
    "started_at": "2025-12-16T14:00:00",
    "finished_at": "2025-12-17T12:00:00",
    "status": "PAID",
    "room_type_name": "Standard Room",
    "room_type_id": 1,
    "resort_name": "Sunset Beach Resort",
    "resort_id": 1
  }
]
```

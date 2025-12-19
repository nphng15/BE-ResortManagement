# API Quản lý Doanh thu Partner

## Tổng quan

Các API dành cho partner quản lý doanh thu, thống kê và rút tiền. Tất cả endpoint đều sử dụng **Bearer Token** để xác thực, không cần truyền `partner_id` trong URL.

## Xác thực

Tất cả các endpoint yêu cầu header:
```
Authorization: Bearer <access_token>
```

Token được lấy từ API đăng nhập `/api/v1/auth/login`.

---

## 1. Thống kê doanh thu

### `GET /api/v1/partner/statistics`

Lấy thông tin thống kê doanh thu và biến động số dư của partner.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/partner/statistics" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "new_bookings_today": 0,
  "monthly_revenue": 2000000.0,
  "total_bookings": 2,
  "current_balance": 1000000.0,
  "balance_movements": {
    "revenues": [
      {
        "invoice_id": 1,
        "booking_detail_id": 1,
        "amount": 2000000.0,
        "time": "2025-12-10T09:54:17.620513",
        "type": "REVENUE"
      }
    ],
    "withdrawals": [
      {
        "id": 1,
        "amount": 500000.0,
        "time": "2025-12-08T09:54:17.632253",
        "type": "WITHDRAW"
      }
    ]
  }
}
```

**Giải thích response:**

| Field | Mô tả |
|-------|-------|
| `new_bookings_today` | Số lượt đặt mới trong ngày |
| `monthly_revenue` | Tổng doanh thu tháng hiện tại |
| `total_bookings` | Tổng số lượt đặt từ trước đến nay |
| `current_balance` | Số dư hiện tại có thể rút |
| `balance_movements.revenues` | Danh sách các khoản thu từ booking |
| `balance_movements.withdrawals` | Danh sách các lần rút tiền |

---

## 2. Lịch đặt phòng

### `GET /api/v1/partner/bookings/schedule`

Lấy lịch đặt phòng của các resort thuộc partner.

**Query Parameters:**

| Param | Type | Mô tả |
|-------|------|-------|
| `start` | datetime | Ngày bắt đầu (YYYY-MM-DD). Mặc định: Thứ 2 tuần này |
| `end` | datetime | Ngày kết thúc (YYYY-MM-DD). Mặc định: Chủ nhật tuần này |
| `resort_id` | int | Lọc theo resort cụ thể (optional) |

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/partner/bookings/schedule?start=2025-12-16&end=2025-12-22" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
[
  {
    "room_id": 1,
    "resort_name": "Resort ABC",
    "room_type": "Deluxe",
    "room_number": "101",
    "started_time": "2025-12-18T14:00:00",
    "finished_time": "2025-12-20T12:00:00"
  }
]
```

---

## 3. Yêu cầu rút tiền

### `POST /api/v1/partner/withdraw`

Tạo yêu cầu rút tiền từ số dư.

**Query Parameters:**

| Param | Type | Mô tả |
|-------|------|-------|
| `amount` | float | Số tiền muốn rút (bắt buộc, > 0) |

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/partner/withdraw?amount=500000" \
  -H "Authorization: Bearer <access_token>"
```

**Response thành công:**
```json
{
  "message": "Yêu cầu rút tiền đã được tạo thành công",
  "withdraw_id": 2,
  "partner_id": 1,
  "requested_amount": 500000.0,
  "remaining_balance": 500000.0,
  "status": "PENDING",
  "created_at": "2025-12-19T10:30:00"
}
```

**Response lỗi (số dư không đủ):**
```json
{
  "detail": "Số dư không đủ để rút tiền"
}
```

---

## Mã lỗi

| Status Code | Mô tả |
|-------------|-------|
| 200 | Thành công |
| 400 | Lỗi request (vd: số dư không đủ) |
| 401 | Token không hợp lệ hoặc hết hạn |
| 403 | Tài khoản không phải là partner |

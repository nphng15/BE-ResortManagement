# Admin Account Management API Documentation

## Tổng quan

API cho phép admin quản lý tài khoản khách hàng và đối tác, bao gồm xem danh sách, cấm (ban) và bỏ cấm (unban) tài khoản.

**Base URL:** `/api/v1/admin/accounts`

---

## 1. Lấy danh sách tài khoản

**Endpoint:** `GET /api/v1/admin/accounts`

**Mô tả:** Lấy danh sách tài khoản khách hàng và đối tác với các bộ lọc.

**Query Parameters:**

| Parameter | Type | Mô tả |
|-----------|------|-------|
| `account_type` | string | Lọc theo loại: `CUSTOMER` hoặc `PARTNER` |
| `status` | string | Lọc theo trạng thái: `ACTIVE`, `BANNED`, `PENDING`, `REJECTED` |
| `search` | string | Tìm kiếm theo username hoặc tên |
| `page` | int | Số trang (mặc định: 1) |
| `page_size` | int | Số bản ghi mỗi trang (mặc định: 20, tối đa: 100) |

**Response (200 OK):**
```json
[
  {
    "account_id": 1,
    "username": "customer01",
    "status": "ACTIVE",
    "account_type": "CUSTOMER",
    "name": "Nguyễn Văn A",
    "phone_number": "0901234567"
  },
  {
    "account_id": 2,
    "username": "partner01",
    "status": "ACTIVE",
    "account_type": "PARTNER",
    "name": "Resort ABC",
    "phone_number": "0909876543"
  }
]
```

**Ví dụ:**
```
GET /api/v1/admin/accounts?account_type=CUSTOMER&status=ACTIVE&page=1&page_size=10
GET /api/v1/admin/accounts?search=nguyen
```

---

## 2. Xem chi tiết tài khoản

**Endpoint:** `GET /api/v1/admin/accounts/{account_id}`

**Mô tả:** Xem thông tin chi tiết của một tài khoản.

**Path Parameters:**

| Parameter | Type | Mô tả |
|-----------|------|-------|
| `account_id` | int | ID của tài khoản |

**Response (200 OK) - Customer:**
```json
{
  "account_id": 1,
  "username": "customer01",
  "status": "ACTIVE",
  "created_at": "2025-12-14T10:30:00",
  "roles": ["CUSTOMER"],
  "customer": {
    "id": 1,
    "fullname": "Nguyễn Văn A",
    "email": "nguyenvana@email.com",
    "phone_number": "0901234567",
    "id_number": "012345678901"
  }
}
```

**Response (200 OK) - Partner:**
```json
{
  "account_id": 2,
  "username": "partner01",
  "status": "ACTIVE",
  "created_at": "2025-12-14T10:30:00",
  "roles": ["PARTNER"],
  "partner": {
    "id": 1,
    "name": "Resort ABC",
    "phone_number": "0909876543",
    "address": "123 Đường ABC, Quận 1, TP.HCM",
    "banking_number": "1234567890",
    "bank": "Vietcombank",
    "balance": 5000000.00
  }
}
```

**Lỗi có thể xảy ra:**
- `404 Not Found` - Không tìm thấy tài khoản

---

## 3. Cấm tài khoản (Ban)

**Endpoint:** `POST /api/v1/admin/accounts/ban`

**Mô tả:** Cấm tài khoản khách hàng hoặc đối tác. Tài khoản bị cấm sẽ không thể đăng nhập.

**Request Body:**
```json
{
  "account_id": 1,
  "reason": "Vi phạm điều khoản sử dụng"
}
```

| Field | Type | Required | Mô tả |
|-------|------|----------|-------|
| `account_id` | int | ✅ | ID của tài khoản cần cấm |
| `reason` | string | ❌ | Lý do cấm (tùy chọn) |

**Response (200 OK):**
```json
{
  "message": "Account has been banned successfully",
  "account_id": 1,
  "status": "BANNED"
}
```

**Lỗi có thể xảy ra:**
- `404 Not Found` - Không tìm thấy tài khoản
- `403 Forbidden` - Không thể cấm tài khoản admin
- `400 Bad Request` - Tài khoản đã bị cấm trước đó

---

## 4. Bỏ cấm tài khoản (Unban)

**Endpoint:** `POST /api/v1/admin/accounts/unban`

**Mô tả:** Bỏ cấm tài khoản, cho phép người dùng đăng nhập lại.

**Request Body:**
```json
{
  "account_id": 1,
  "reason": "Đã xác minh và giải quyết vấn đề"
}
```

| Field | Type | Required | Mô tả |
|-------|------|----------|-------|
| `account_id` | int | ✅ | ID của tài khoản cần bỏ cấm |
| `reason` | string | ❌ | Lý do bỏ cấm (tùy chọn) |

**Response (200 OK):**
```json
{
  "message": "Account has been unbanned successfully",
  "account_id": 1,
  "status": "ACTIVE"
}
```

**Lỗi có thể xảy ra:**
- `404 Not Found` - Không tìm thấy tài khoản
- `400 Bad Request` - Tài khoản không ở trạng thái bị cấm

---

## Account Status

| Status | Mô tả | Có thể đăng nhập |
|--------|-------|------------------|
| `ACTIVE` | Tài khoản hoạt động bình thường | ✅ |
| `BANNED` | Tài khoản bị cấm | ❌ |
| `PENDING` | Đang chờ admin duyệt (đối tác) | ❌ |
| `REJECTED` | Bị từ chối đăng ký | ❌ |

---

## Lưu ý

- Không thể cấm tài khoản có role `ADMIN`
- Khi tài khoản bị cấm, người dùng sẽ nhận thông báo: "Account has been banned. Please contact support." khi cố đăng nhập
- Token hiện tại của tài khoản bị cấm vẫn còn hiệu lực cho đến khi hết hạn, nhưng không thể tạo token mới

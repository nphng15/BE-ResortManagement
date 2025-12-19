# API Thông tin tài khoản

## 1. Lấy thông tin người dùng hiện tại

**Endpoint:** `GET /api/v1/auth/me`

**Headers:**
```
Authorization: Bearer <token>
```

**Response cho Customer (200):**
```json
{
  "account_id": 1,
  "username": "user123",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00",
  "roles": ["CUSTOMER"],
  "customer": {
    "id": 1,
    "fullname": "Nguyễn Văn A",
    "email": "email@example.com",
    "phone_number": "0901234567",
    "id_number": "012345678901"
  }
}
```

**Response cho Partner (200):**
```json
{
  "account_id": 2,
  "username": "partner123",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00",
  "roles": ["PARTNER"],
  "partner": {
    "id": 1,
    "name": "Resort ABC",
    "phone_number": "0901234567",
    "address": "123 Đường ABC, Quận 1, TP.HCM",
    "banking_number": "1234567890",
    "bank": "Vietcombank",
    "balance": 1000000.00
  }
}
```

**Response lỗi:**
- `401` - Token không hợp lệ hoặc hết hạn

---

# API Cập nhật thông tin tài khoản

## 1. Cập nhật thông tin Customer

**Endpoint:** `PUT /api/v1/auth/me/customer`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "fullname": "Nguyễn Văn A",
  "email": "email@example.com",
  "phone_number": "0901234567",
  "id_number": "012345678901"
}
```

> Tất cả các field đều optional, chỉ cần truyền field muốn cập nhật.

**Response thành công (200):**
```json
{
  "message": "Cập nhật thông tin thành công",
  "customer": {
    "id": 1,
    "fullname": "Nguyễn Văn A",
    "email": "email@example.com",
    "phone_number": "0901234567",
    "id_number": "012345678901"
  }
}
```

**Response lỗi:**
- `401` - Token không hợp lệ
- `400` - Tài khoản không phải là customer

---

## 2. Cập nhật thông tin Partner

**Endpoint:** `PUT /api/v1/auth/me/partner`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Resort ABC",
  "phone_number": "0901234567",
  "address": "123 Đường ABC, Quận 1, TP.HCM",
  "banking_number": "1234567890",
  "bank": "Vietcombank"
}
```

> Tất cả các field đều optional, chỉ cần truyền field muốn cập nhật.

**Response thành công (200):**
```json
{
  "message": "Cập nhật thông tin thành công",
  "partner": {
    "id": 1,
    "name": "Resort ABC",
    "phone_number": "0901234567",
    "address": "123 Đường ABC, Quận 1, TP.HCM",
    "banking_number": "1234567890",
    "bank": "Vietcombank"
  }
}
```

**Response lỗi:**
- `401` - Token không hợp lệ
- `400` - Tài khoản không phải là partner

---

## 3. Đổi mật khẩu

**Endpoint:** `PUT /api/v1/auth/me/password`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "old_password": "matkhaucu123",
  "new_password": "matkhaumoi456"
}
```

**Response thành công (200):**
```json
{
  "message": "Đổi mật khẩu thành công"
}
```

**Response lỗi:**
- `401` - Token không hợp lệ
- `400` - Mật khẩu cũ không đúng

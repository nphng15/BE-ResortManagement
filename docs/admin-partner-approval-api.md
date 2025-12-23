# Admin Partner Approval API Documentation

## Tổng quan

API quản lý phê duyệt đối tác dành cho Admin. Cho phép xem danh sách đối tác đang chờ duyệt và duyệt/từ chối yêu cầu đăng ký.

**Base URL:** `/api/v1/admin/partners`

**Yêu cầu xác thực:** Tất cả API đều yêu cầu token của tài khoản có role `ADMIN`

**Headers bắt buộc:**
```
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

---

## 1. Lấy danh sách đối tác chờ duyệt

**Endpoint:** `GET /api/v1/admin/partners/pending`

**Mô tả:** Lấy danh sách tất cả đối tác có trạng thái `PENDING` đang chờ admin duyệt.

### Request

```http
GET /api/v1/admin/partners/pending HTTP/1.1
Host: your-api-domain.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response

**Success (200 OK):**
```json
[
  {
    "id": 1,
    "account_id": 5,
    "name": "Resort Biển Xanh",
    "phone_number": "0901234567",
    "address": "123 Đường Trần Phú, Nha Trang",
    "banking_number": "1234567890123",
    "bank": "Vietcombank",
    "account_status": "PENDING"
  },
  {
    "id": 2,
    "account_id": 6,
    "name": "Khách sạn Sao Mai",
    "phone_number": "0912345678",
    "address": "456 Đường Nguyễn Huệ, Đà Nẵng",
    "banking_number": "9876543210987",
    "bank": "Techcombank",
    "account_status": "PENDING"
  }
]
```

**Empty List (200 OK):**
```json
[]
```

### Response Fields

| Field | Type | Mô tả |
|-------|------|-------|
| `id` | integer | ID của partner profile |
| `account_id` | integer | ID của account (dùng để duyệt/từ chối) |
| `name` | string | Tên đối tác/resort |
| `phone_number` | string | Số điện thoại liên hệ |
| `address` | string | Địa chỉ |
| `banking_number` | string | Số tài khoản ngân hàng |
| `bank` | string | Tên ngân hàng |
| `account_status` | string | Trạng thái tài khoản (`PENDING`) |

### Errors

| Status Code | Mô tả |
|-------------|-------|
| `401 Unauthorized` | Token không hợp lệ hoặc hết hạn |
| `403 Forbidden` | Tài khoản không có quyền ADMIN |

---

## 2. Duyệt/Từ chối đối tác

**Endpoint:** `POST /api/v1/admin/partners/approve`

**Mô tả:** Duyệt hoặc từ chối yêu cầu đăng ký của đối tác.

### Request

```http
POST /api/v1/admin/partners/approve HTTP/1.1
Host: your-api-domain.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "account_id": 5,
  "approved": true
}
```

### Request Body

| Field | Type | Required | Mô tả |
|-------|------|----------|-------|
| `account_id` | integer | ✅ | ID của account cần duyệt (lấy từ API pending) |
| `approved` | boolean | ✅ | `true` = duyệt, `false` = từ chối |

### Response

**Duyệt thành công (200 OK):**
```json
{
  "message": "Partner registration approved successfully",
  "account_id": 5,
  "status": "ACTIVE"
}
```

**Từ chối thành công (200 OK):**
```json
{
  "message": "Partner registration rejected successfully",
  "account_id": 5,
  "status": "REJECTED"
}
```

### Response Fields

| Field | Type | Mô tả |
|-------|------|-------|
| `message` | string | Thông báo kết quả |
| `account_id` | integer | ID của account đã xử lý |
| `status` | string | Trạng thái mới (`ACTIVE` hoặc `REJECTED`) |

### Errors

| Status Code | Response | Mô tả |
|-------------|----------|-------|
| `401 Unauthorized` | `{"detail": "Not authenticated"}` | Token không hợp lệ |
| `403 Forbidden` | `{"detail": "Admin access required"}` | Không có quyền ADMIN |
| `404 Not Found` | `{"detail": "Pending partner account not found"}` | Account không tồn tại hoặc không ở trạng thái PENDING |

---

## Flow sử dụng cho Frontend

```
┌─────────────────────────────────────────────────────────────┐
│                    ADMIN DASHBOARD                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Gọi GET /pending để lấy danh sách                      │
│     ↓                                                       │
│  2. Hiển thị danh sách đối tác chờ duyệt                   │
│     ↓                                                       │
│  3. Admin click "Duyệt" hoặc "Từ chối"                     │
│     ↓                                                       │
│  4. Gọi POST /approve với account_id và approved           │
│     ↓                                                       │
│  5. Refresh danh sách (gọi lại GET /pending)               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Code Examples

### JavaScript/Fetch

```javascript
// Lấy danh sách pending
const getPendingPartners = async (token) => {
  const response = await fetch('/api/v1/admin/partners/pending', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.json();
};

// Duyệt đối tác
const approvePartner = async (token, accountId, approved) => {
  const response = await fetch('/api/v1/admin/partners/approve', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      account_id: accountId,
      approved: approved
    })
  });
  return response.json();
};
```

### React Hook Example

```javascript
const usePartnerApproval = () => {
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(false);
  const token = useAuthToken();

  const fetchPending = async () => {
    setLoading(true);
    try {
      const data = await getPendingPartners(token);
      setPending(data);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (accountId) => {
    await approvePartner(token, accountId, true);
    fetchPending(); // Refresh list
  };

  const handleReject = async (accountId) => {
    await approvePartner(token, accountId, false);
    fetchPending(); // Refresh list
  };

  return { pending, loading, fetchPending, handleApprove, handleReject };
};
```

---

## Account Status Reference

| Status | Mô tả | Có thể đăng nhập |
|--------|-------|------------------|
| `PENDING` | Đang chờ admin duyệt | ❌ |
| `ACTIVE` | Đã được duyệt, hoạt động bình thường | ✅ |
| `REJECTED` | Bị từ chối | ❌ |
| `BANNED` | Bị cấm | ❌ |

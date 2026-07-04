# 🌐 Cổng Nhân Viên – Employee Portal
### Nhóm 5 | Quản lý Tài sản + Tài chính

Web app cho nhân viên tự xem tài sản, tạo đơn mượn – không cần vào Odoo admin.

---

## 🚀 Cách mở

1. Đảm bảo Odoo đang chạy tại `http://localhost:8069`
2. Mở file `index.html` trực tiếp trong Chrome/Firefox

---

## 👤 Tài khoản mặc định

| Nhân viên | Username | Mật khẩu |
|---|---|---|
| Lê Ngọc Minh | `nv001` | `123456` |
| Nguyễn Quang Trung | `nv002` | `123456` |
| Đỗ Khánh Hùng | `nv003` | `123456` |
| Nguyễn Vũ Yến Nhi | `nv004` | `123456` |
| Lê Thị Vân Anh | `nv005` | `123456` |
| Nguyễn Văn Tấn | `nv006` | `123456` |
| Nguyễn Quốc Việt | `nv007` | `123456` |

---

## 📋 Chức năng

| Trang | Chức năng |
|---|---|
| 🏠 Tổng quan | Thống kê nhanh: số tài sản, đơn mượn, quá hạn |
| 👤 Hồ sơ | Xem thông tin cá nhân, phòng ban, chức vụ |
| 📦 Tài sản của tôi | Danh sách tài sản đang được phân bổ |
| 📋 Đơn mượn | Lịch sử đơn mượn, trạng thái, cảnh báo quá hạn |
| ➕ Tạo đơn mượn | Tạo và gửi đơn mượn tài sản |
| 🔑 Đổi mật khẩu | Đổi mật khẩu đăng nhập web |

---

## ⚙️ Đổi URL Odoo

Nếu Odoo chạy ở port khác, sửa dòng đầu trong `index.html`:
```javascript
const ODOO_URL = 'http://localhost:8071'; // ← đổi ở đây
```

---

## 🔧 Thêm nhân viên mới

Trong Odoo admin: **QLNS → Nhân viên → Tab "Tài khoản Web"**
- Điền **Tên đăng nhập web**
- Bật toggle **Web Active**
- Mật khẩu mặc định: `123456` (nhân viên đổi sau)

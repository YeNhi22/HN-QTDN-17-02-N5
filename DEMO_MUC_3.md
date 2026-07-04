# 🥇 DEMO MỨC 3 — AI CHATBOT & DASHBOARD

**Tiêu chí**: Hệ thống có AI Chatbot 24/7 trả lời dựa trên Knowledge Base + dữ liệu thực từ DB. Dashboard real-time tổng hợp từ tất cả modules.

---

## PHẦN 1 — DASHBOARD TỔNG QUAN

### Truy cập
**Menu → 🏠 Trang chủ → 📊 Dashboard**

### Những gì cần chứng minh

👉 **Thẻ thống kê real-time** (lấy từ DB, không hardcode):
- Tổng tài sản
- Đơn chờ duyệt
- Đang mượn
- Tổng giá trị

👉 **Thao tác nhanh**:
- Tạo đơn mượn
- Duyệt đơn
- Xem tài sản
- Kiểm kê
- Phê duyệt mua
- Scan hóa đơn

👉 **Thông báo** — hiện cảnh báo quá hạn, đơn chờ duyệt

👉 **Hoạt động gần đây** — log realtime từ DB

**Điểm nhấn**: Tạo thêm 1 đơn mượn mới → quay lại Dashboard → số **Đơn chờ duyệt** tăng lên ngay.

---

## PHẦN 2 — AI CHATBOT

### Truy cập
**Menu → 🏠 Trang chủ → 🤖 AI Chatbot**

### Cài đặt API Key (nếu chưa có)

**Cách 1 — Qua Odoo Settings:**
```
Menu → Thiết lập → Cấu hình → Trang chủ Settings
→ Điền Gemini API Key
→ Lưu
```

**Cách 2 — Qua biến môi trường (Docker):**
```bash
# Trong docker-compose.yml đã có sẵn:
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

> AI ưu tiên dùng **Groq** (model llama-3.3-70b-versatile, nhanh hơn).  
> Fallback: **Gemini 2.0 Flash** nếu Groq không khả dụng.

---

### Câu hỏi demo — Quy trình nghiệp vụ

```
Quy trình mượn tài sản là gì?
```
→ AI mô tả đầy đủ luồng: Tạo đơn → Gửi duyệt → Phê duyệt → Nhận TS → Trả TS

```
Cách đề xuất mua tài sản mới như thế nào?
```
→ AI hướng dẫn từng bước: Vào module nào, điền gì, bấm nút nào

```
Quy chế sử dụng tài sản công ty?
```
→ AI trả lời từ Knowledge Base đã được cấu hình

---

### Câu hỏi demo — Dữ liệu thực từ DB

```
Có bao nhiêu tài sản trong hệ thống hiện tại?
```
→ AI trả về số liệu thực từ DB

```
Hiện có bao nhiêu đơn mượn đang chờ duyệt?
```
→ AI đọc dữ liệu real-time và trả lời

```
Tài sản nào đang được giao cho tôi?
```
→ AI tra cứu theo user đang đăng nhập

---

### Câu hỏi demo — Hỏi tự do

```
Làm thế nào để thanh lý tài sản hư hỏng?
```

```
Chính sách bảo hành tài sản như thế nào?
```

```
Khi nào cần làm kiểm kê tài sản định kỳ?
```

**Điểm nhấn kỹ thuật:**
- AI **không hardcode** câu trả lời — đọc từ Knowledge Base + truy vấn DB
- Lịch sử hội thoại được lưu theo user tại **Quản lý Chatbot → Lịch sử hội thoại**

---

## PHẦN 3 — SCAN HÓA ĐƠN (OCR)

### Truy cập
**Menu → 🏠 Trang chủ → 📷 Scan hóa đơn**

→ Upload ảnh hóa đơn (JPG/PNG/PDF)  
→ AI Gemini Vision phân tích ảnh  
→ Trích xuất: tên hàng, số lượng, đơn giá, tổng tiền, nhà cung cấp

→ Kết quả lưu tại: **Menu → 🏠 Trang chủ → 📋 Lịch sử OCR**

---

## PHẦN 4 — EMPLOYEE PORTAL (Web App Nhân viên)

### Truy cập
```
http://localhost:8069/portal
```
Hoặc mở trực tiếp file `employee_portal/index.html` trong trình duyệt.

### Đăng nhập
| Username | Mật khẩu | Nhân viên |
|----------|----------|-----------|
| nv001 | 123456 | Lê Ngọc Minh |
| nv002 | 123456 | Nguyễn Quang Trung |
| nv003 | 123456 | Đỗ Khánh Hùng |

### Demo các tính năng
- **🏠 Tổng quan** — xem stats nhanh của nhân viên đó
- **👤 Hồ sơ** — xem thông tin cá nhân, phòng ban, chức vụ (lấy từ HRM)
- **📦 Tài sản của tôi** — tài sản đang được phân bổ
- **📋 Đơn mượn** — lịch sử, cảnh báo quá hạn
- **➕ Tạo đơn mượn** — tạo đơn từ portal, xác nhận bên Odoo admin
- **🔑 Đổi mật khẩu** — đổi mật khẩu web

---

## QUẢN LÝ CHATBOT KNOWLEDGE BASE

### Thêm nội dung mới vào KB
**Menu → 🏠 Trang chủ → ⚙️ Quản lý Chatbot → 📚 Cơ sở tri thức → Tạo**

```
Tiêu đề  : Quy trình xử lý tài sản hư hỏng
Nội dung : [Mô tả chi tiết quy trình]
Loại     : Quy trình
Tags     : tai_san, bao_tri, hu_hong
```

### Thêm FAQ
**Menu → ⚙️ Quản lý Chatbot → ❓ FAQ → Tạo**

```
Câu hỏi  : Mượn tài sản tối đa bao nhiêu ngày?
Câu trả lời: Tối đa 30 ngày, có thể gia hạn nếu được phê duyệt.
```

---

## BẢNG TỔNG KẾT MỨC 3

| Tính năng | Truy cập | Điểm cần chứng minh |
|-----------|---------|---------------------|
| Dashboard | Trang chủ → Dashboard | Stats real-time từ DB |
| AI Chatbot | Trang chủ → AI Chatbot | Trả lời từ KB + dữ liệu thực |
| OCR Hóa đơn | Trang chủ → Scan hóa đơn | Phân tích ảnh hóa đơn |
| Employee Portal | localhost:8069/portal | NV tự xem TS, tạo đơn mượn |
| Lịch sử hội thoại | Quản lý Chatbot | Lưu per-user |

---

*Demo Mức 3 | HN-QTDN-17-02-N5 | Odoo 15*

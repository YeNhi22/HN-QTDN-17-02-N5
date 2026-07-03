# 🚀 HƯỚNG DẪN SETUP A-Z — ODOO 15 PORT 8069

**Thực hiện trong Ubuntu/WSL terminal**

---

## PHẦN 1: CÀI ĐẶT LẦN ĐẦU

### Bước 1: Mở Terminal Ubuntu

Nhấn `Win` → tìm **Ubuntu** → mở

### Bước 2: Vào thư mục project

```bash
cd /mnt/e/HN-QTDN-17-02-N5
```

### Bước 3: Kill port nếu đang bị chiếm

```bash
fuser -k 8069/tcp 2>/dev/null; echo "OK"
```

### Bước 4: Khởi động Odoo lần đầu (chưa có database)

```bash
python3 odoo-bin.py -c odoo.conf
```

Chờ thấy:
```
INFO ? odoo.service.server: HTTP service (werkzeug) running on 0.0.0.0:8069
```

---

## PHẦN 2: TẠO DATABASE MỚI

### Bước 5: Mở trình quản lý database

Mở Chrome/Firefox, vào: **http://localhost:8069/web/database/manager**

### Bước 6: Tạo database

Click **"Create Database"** và điền:

```
Master Password : admin123
Database Name   : quan_ly_btl
Email           : admin@admin.com
Password        : admin
Phone           : (để trống)
Language        : Vietnamese (Tiếng Việt)
Country         : Vietnam
Demo Data       : ✅ Bỏ tick (KHÔNG lấy demo)
```

Click **"Create Database"** → chờ 2-3 phút

### Bước 7: Đăng nhập

Sau khi tạo xong, trang tự chuyển về:
- **Email**: `admin@admin.com`
- **Password**: `admin`

→ Đăng nhập thành công → thấy giao diện Odoo

---

## PHẦN 3: CÀI MODULES THEO THỨ TỰ

> ⚠️ **QUAN TRỌNG**: Phải cài đúng thứ tự, đợi cài xong từng cái

### Bước 8: Update danh sách Apps

```
Menu trên cùng → Apps → (click vào Apps)
→ Bấm nút "Update Apps List" (góc trên)
→ Bấm "Update" trong popup xác nhận
→ Chờ ~30 giây
```

### Bước 9: Cài Module 1 — Nhân sự

```
Apps → Search: "nhan_su"
→ Tìm thấy module "nhan_su"
→ Bấm [Install]
→ Chờ cài xong (2-5 phút)
```

### Bước 10: Cài Module 2 — Tài sản

```
Apps → Search: "quan_ly_tai_san"
→ Bấm [Install]
→ Chờ cài xong
```

### Bước 11: Cài Module 3 — Tài chính

```
Apps → Search: "quan_ly_tai_chinh"
→ Bấm [Install]
→ Chờ cài xong
```

### Bước 12: Cài Module Trang chủ (Dashboard + AI)

```
Apps → Search: "q_trang_chu" hoặc "Trang chủ"
→ Bấm [Install]
→ Chờ cài xong
```

---

## PHẦN 4: NHẬP DỮ LIỆU MẪU

> Xem file `DU_LIEU_MAU_NHAP.md` để biết chi tiết

### Bước 13: Nhập Phòng ban

```
Menu → QLNS → Quản lý phòng ban → Tạo
  IT    | Phòng Công nghệ thông tin
  KT    | Phòng Kế toán
  HCNS  | Phòng Hành chính - Nhân sự
```

### Bước 14: Nhập Chức vụ

```
Menu → QLNS → Quản lý chức vụ → Tạo
  GD  | Giám đốc
  TP  | Trưởng phòng
  NV  | Nhân viên
```

### Bước 15: Nhập Nhân viên

```
Menu → QLNS → Quản lý nhân viên → Tạo
  NV001 | Nguyễn Văn An | IT | Trưởng phòng
  NV002 | Trần Thị Bình | IT | Nhân viên
  NV003 | Lê Minh Cường | KT | Kế toán viên
```

→ Mỗi nhân viên: Tab "Lịch sử công tác" → Thêm dòng

### Bước 16: Nhập Loại tài sản

```
Menu → Quản lý tài sản → Tài sản → Loại tài sản → Tạo
  PC     | Máy tính & Laptop
  OFFICE | Thiết bị văn phòng
```

### Bước 17: Nhập Tài sản

```
Menu → Quản lý tài sản → Tài sản → Quản lý tài sản cụ thể → Tạo
  TS001 | Laptop Dell Latitude | PC | 25,000,000đ | Tuyến tính | 5 năm
  TS002 | Laptop HP ProBook    | PC | 20,000,000đ | Tuyến tính | 5 năm
  TS003 | Máy in Canon        | OFFICE | 5,500,000đ | Tuyến tính | 7 năm
```

### Bước 18: Phân bổ tài sản

```
Menu → Quản lý tài sản → Tài sản → Phân bổ tài sản → Tạo
  TS001 → Chọn Nhân viên: Nguyễn Văn An → Phòng ban TỰ ĐIỀN [MỨC 1]
  TS002 → Chọn Nhân viên: Trần Thị Bình → Phòng ban TỰ ĐIỀN [MỨC 1]
  TS003 → Chọn Nhân viên: Lê Minh Cường → Phòng ban TỰ ĐIỀN [MỨC 1]
```

---

## PHẦN 5: DEMO 3 MỨC

### 🥉 MỨC 1 — Tích hợp HRM (Cơ bản)

**Demo**: Dữ liệu nhân sự là nguồn gốc

```
1. Tạo nhân viên với lịch sử công tác
   → Phòng ban hiện tại TỰ TÍNH từ lịch sử [KHÔNG nhập tay]

2. Phân bổ tài sản
   → Chọn nhân viên → Phòng ban TỰ ĐIỀN từ HRM
   [Tích hợp HRM → Tài sản, không trùng lặp dữ liệu]

3. Báo cáo Tài chính
   → Chọn phòng ban → Lọc chi phí theo đúng phòng ban HRM
   [HRM → Tài chính: cùng 1 nguồn dữ liệu phòng ban]
```

### 🥈 MỨC 2 — Tự động hóa (Khá)

**Demo**: Event-driven automation

```
Luồng 1: Đề xuất mua → Phê duyệt → TỰ ĐỘNG

  Tài sản → Đề xuất mua → Tạo → Gửi đề xuất
       ↓ TỰ ĐỘNG
  Tài chính → Phê duyệt → Bấm [Phê duyệt]
       ↓ TỰ ĐỘNG (không cần làm gì thêm)
  ✅ Tạo tài sản trong module Tài sản
  ✅ Ghi bút toán kế toán (Nợ 211 / Có 112)
  ✅ Tạo lịch khấu hao
  ✅ Ghi kế toán quản trị

Luồng 2: Đơn mượn → Gửi duyệt → TỰ ĐỘNG

  Đơn mượn → Gửi duyệt
       ↓ TỰ ĐỘNG
  ✅ Tạo Phiếu mượn trả ở màn hình Quản lý

Luồng 3: Báo cáo TC → Tính toán → TỰ ĐỘNG

  Báo cáo → Bấm [Tính toán & Đồng bộ Khấu hao]
       ↓ TỰ ĐỘNG
  ✅ Chi phí khấu hao lấy từ module Tài sản
```

### 🥇 MỨC 3 — AI & Chatbot (Giỏi)

**Demo**: AI Chatbot tích hợp

```
Menu → 🏠 Trang chủ → 🤖 AI Chatbot
→ Hỏi: "Quy trình mượn tài sản là gì?"
→ Hỏi: "Có bao nhiêu tài sản trong hệ thống?"
→ Hỏi: "Cách đề xuất mua tài sản mới?"

AI trả lời dựa trên:
✅ Knowledge Base trong hệ thống
✅ Dữ liệu thực từ database
✅ Quy trình nghiệp vụ đã cấu hình
```

---

## PHẦN 6: CHẠY HÀNG NGÀY

### Khởi động server

```bash
cd /mnt/e/HN-QTDN-17-02-N5
fuser -k 8069/tcp 2>/dev/null
python3 odoo-bin.py -c odoo.conf
```

→ Vào **http://localhost:8069**
→ Đăng nhập: `admin@admin.com` / `admin`

### Khi sửa code Python/XML

```bash
# Ctrl+C dừng server, sau đó:
python3 odoo-bin.py -c odoo.conf -u quan_ly_tai_san
# Hoặc update tất cả:
python3 odoo-bin.py -c odoo.conf -u nhan_su,quan_ly_tai_san,quan_ly_tai_chinh,q_trang_chu
```

---

## PHẦN 7: XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi 1: Port 8069 đang bị chiếm
```bash
fuser -k 8069/tcp
python3 odoo-bin.py -c odoo.conf
```

### Lỗi 2: Không kết nối được database
```bash
# Kiểm tra PostgreSQL đang chạy không
pg_isready -h 127.0.0.1 -p 5434 -U odoo
# Nếu không chạy:
sudo service postgresql start
```

### Lỗi 3: Module không cài được
```bash
# Xem log lỗi chi tiết
python3 odoo-bin.py -c odoo.conf --log-level=debug 2>&1 | grep ERROR
```

### Lỗi 4: Bút toán lỗi khi phê duyệt mua
```
Tài chính → Kế toán → Cấu hình → Sơ đồ tài khoản
→ Import Vietnam Chart of Accounts
→ Thử phê duyệt lại
```

### Lỗi 5: Sequence trùng mã
```bash
# Database đã được fix trong code mới
# Chỉ cần upgrade:
python3 odoo-bin.py -c odoo.conf -u quan_ly_tai_san
```

---

## PHẦN 8: KIỂM TRA SAU KHI CÀI

| Kiểm tra | Kết quả mong đợi |
|----------|-----------------|
| **Menu** | QLNS, Quản lý tài sản, Quản lý tài chính, Trang chủ |
| **Nhân sự** | Phòng ban hiện tại tự tính từ lịch sử công tác |
| **Phân bổ TS** | Chọn NV → Phòng ban tự điền |
| **Đơn mượn** | Gửi duyệt → Tự tạo phiếu mượn trả |
| **Đề xuất mua** | Phê duyệt → Tự tạo TS + Bút toán + KH |
| **Dashboard** | Hiện stats realtime |
| **AI Chatbot** | Trả lời câu hỏi nghiệp vụ |

---

## TÓM TẮT LỆNH QUAN TRỌNG

```bash
# Chạy bình thường
python3 odoo-bin.py -c odoo.conf

# Cài module mới
python3 odoo-bin.py -c odoo.conf -i TEN_MODULE

# Update module sau khi sửa code
python3 odoo-bin.py -c odoo.conf -u TEN_MODULE

# Update tất cả custom modules
python3 odoo-bin.py -c odoo.conf -u nhan_su,quan_ly_tai_san,quan_ly_tai_chinh,q_trang_chu

# Kill port đang dùng
fuser -k 8069/tcp

# Xem log lỗi
python3 odoo-bin.py -c odoo.conf 2>&1 | grep -E "ERROR|CRITICAL"
```

---

**URL**: http://localhost:8069  
**Login**: admin@admin.com / admin  
**DB Manager**: http://localhost:8069/web/database/manager (pass: admin123)

---

*Setup guide | HN-QTDN-17-02-N5 | Odoo 15*

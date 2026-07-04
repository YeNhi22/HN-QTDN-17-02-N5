# 🥉 DEMO MỨC 1 — TÍCH HỢP HRM

**Tiêu chí**: Nhân sự là nguồn dữ liệu gốc (Single Source of Truth).  
Phòng ban/chức vụ tự động đồng bộ sang Tài sản và Tài chính — không nhập tay.

---

## ĐIỂM CẦN CHỨNG MINH

1. Nhân viên có lịch sử công tác → **Phòng ban hiện tại tự tính**, không nhập tay
2. Phân bổ tài sản → chọn nhân viên → **Phòng ban tự điền** từ HRM
3. Báo cáo tài chính → chọn phòng ban → lọc đúng theo HRM

---

## CHUẨN BỊ DỮ LIỆU (nếu chưa có)

### 1. Tạo Phòng ban
**Menu → QLNS → Quản lý phòng ban → Tạo**

| Mã | Tên |
|----|-----|
| IT | Phòng Công nghệ thông tin |
| KT | Phòng Kế toán |
| HCNS | Phòng Hành chính - Nhân sự |

### 2. Tạo Chức vụ
**Menu → QLNS → Quản lý chức vụ → Tạo**

| Mã | Tên |
|----|-----|
| TP | Trưởng phòng |
| NV | Nhân viên |
| KTV | Kế toán viên |

### 3. Tạo Nhân viên
**Menu → QLNS → Quản lý nhân viên → Tạo**

```
Mã định danh : NV001
Họ tên       : Nguyễn Văn An
Email        : an@company.com
```

→ Tab **Lịch sử công tác** → Thêm dòng:
```
Phòng ban   : IT
Chức vụ     : Trưởng phòng
Thời gian bắt đầu: 01/01/2023
Thời gian kết thúc: 31/12/2099
```

→ **Lưu**

### 4. Tạo Tài sản
**Menu → Quản lý tài sản → Tài sản → Loại tài sản → Tạo**
```
Mã: PC | Tên: Máy tính & Laptop
```

**Menu → Quản lý tài sản → Tài sản → Quản lý tài sản cụ thể → Tạo**
```
Mã tài sản       : TS001
Tên tài sản      : Laptop Dell Latitude 5520
Loại tài sản     : Máy tính & Laptop
Ngày mua         : 01/01/2024
Giá trị ban đầu  : 25,000,000
Phương pháp KH   : Tuyến tính
Thời gian SD tối đa: 5
```

---

## DEMO BƯỚC 1 — Phòng ban tự tính từ lịch sử công tác

**Menu → QLNS → Quản lý nhân viên → mở NV001**

👉 **Chỉ ra**: Trường **"Phòng ban hiện tại"** hiển thị **IT** — tự tính từ lịch sử công tác, không nhập tay.

**Điểm nhấn kỹ thuật**: Field `phong_ban_hien_tai_id` là `compute + store=True`, tự cập nhật khi lịch sử thay đổi.

---

## DEMO BƯỚC 2 — Phân bổ tài sản: phòng ban tự điền

**Menu → Quản lý tài sản → Tài sản → Phân bổ tài sản → Tạo**

```
Tài sản              : Laptop Dell Latitude 5520 (TS001)
Nhân viên sử dụng    : [chọn Nguyễn Văn An]
```

👉 **Ngay khi chọn nhân viên**: Trường **Phòng ban** tự điền **IT** — không cần nhập tay.

**Điểm nhấn**: `@api.onchange('nhan_vien_su_dung_id')` đọc `phong_ban_hien_tai_id` từ HRM → auto-fill.

```
Ngày phân bổ  : (hôm nay)
Trạng thái    : Đang sử dụng
Tình trạng    : Bình thường
```
→ **Lưu**

---

## DEMO BƯỚC 3 — Báo cáo tài chính lọc theo phòng ban HRM

**Menu → Quản lý tài chính → Báo cáo tài chính → Tạo**

```
Tên báo cáo  : Báo cáo tháng 6/2026 - Phòng IT
Tháng / Năm  : 6 / 2026
Phòng ban    : IT    ← chọn phòng ban từ HRM
Doanh thu    : 500,000,000
Chi phí lương: 150,000,000
```

→ Bấm **[⚡ Tính toán & Đồng bộ Khấu hao]**

👉 **Chi phí khấu hao tự điền** — lấy từ tài sản đang phân bổ cho phòng IT.

**Điểm nhấn**: Cùng 1 nguồn dữ liệu phòng ban từ HRM → không trùng lặp, không sai.

---

## BẢNG TỔNG KẾT MỨC 1

| Chứng minh | Thao tác | Kết quả mong đợi |
|-----------|---------|-----------------|
| HRM là nguồn gốc | Xem NV001 | Phòng ban IT tự hiện, không nhập tay |
| HRM → Tài sản | Phân bổ TS, chọn NV | Phòng ban IT tự điền ngay |
| HRM → Tài chính | Báo cáo TC, chọn PB | KH tự đồng bộ từ tài sản phòng IT |

---

*Demo Mức 1 | HN-QTDN-17-02-N5 | Odoo 15*

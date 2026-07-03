# 📊 DỮ LIỆU TEST - HƯỚNG DẪN IMPORT

## 📁 CẤU TRÚC FILES

```
test_data/
├── phong_ban.csv          # 5 phòng ban
├── chuc_vu.csv            # 6 chức vụ
├── nhan_vien.csv          # 10 nhân viên
├── danh_muc_tai_san.csv   # 5 danh mục
├── tai_san.csv            # 20 tài sản
└── README_TEST_DATA.md    # File này
```

---

## 🚀 CÁCH IMPORT (2 PHƯƠNG PHÁP)

### Phương pháp 1: Import CSV trong Odoo UI

**Bước 1**: Vào module cần import
```
Ví dụ: Menu → Nhân sự → Cấu hình → Phòng ban
```

**Bước 2**: Click **Favorites** (⭐) → **Import records**

**Bước 3**: Upload file CSV:
- Click **Upload File**
- Chọn file `phong_ban.csv`
- Click **Test**

**Bước 4**: Map fields (nếu cần):
- Odoo tự động map nếu tên cột khớp
- Kiểm tra preview data

**Bước 5**: Click **Import**

**Bước 6**: Lặp lại cho các file khác theo thứ tự:
```
1. phong_ban.csv
2. chuc_vu.csv
3. nhan_vien.csv
4. danh_muc_tai_san.csv
5. tai_san.csv
```

---

### Phương pháp 2: Nhập thủ công

Xem hướng dẫn chi tiết trong:
- `HUONG_DAN_SU_DUNG.md` (đầy đủ)
- `QUICK_START_GUIDE.md` (tóm tắt)

---

## 📋 DỮ LIỆU MẪU

### 1. Phòng ban (5 phòng)
- IT: Công nghệ thông tin
- KT: Kế toán
- HCNS: Hành chính - Nhân sự
- KD: Kinh doanh
- MKT: Marketing

### 2. Chức vụ (6 chức vụ)
- GD: Giám đốc
- TP: Trưởng phòng
- DEV: Lập trình viên
- KTV: Kế toán viên
- NVKD: Nhân viên kinh doanh
- NVHC: Nhân viên hành chính

### 3. Nhân viên (10 người)
- NV001-NV010
- Đầy đủ: Tên, Email, SĐT, Ngày sinh
- Có phân công phòng ban + chức vụ

### 4. Danh mục tài sản (5 danh mục)
- PC: Máy tính (5 năm)
- OFFICE: Thiết bị văn phòng (7 năm)
- NETWORK: Thiết bị mạng (7 năm)
- VEHICLE: Phương tiện (10 năm)
- ELEC: Điện tử (3 năm)

### 5. Tài sản (20 tài sản)
- TS001-TS020
- Giá trị: 5M - 500M VND
- Đầy đủ: Tên, Mã, Serial, Ngày mua

---

## ✅ KIỂM TRA SAU KHI IMPORT

### Dashboard kiểm tra
```
Menu → Trang chủ → Dashboard
```

Phải hiển thị:
- ✅ Tổng tài sản: 20
- ✅ Nhân viên: 10
- ✅ Phòng ban: 5

### Tree view kiểm tra
```
Menu → Nhân sự → Nhân viên
```
- Hiển thị 10 nhân viên
- Mỗi người có phòng ban hiện tại
- Có chức vụ hiện tại

---

## 🐛 LỖI THƯỜNG GẶP

### Lỗi: "Required field missing"
**Nguyên nhân**: Thiếu trường bắt buộc

**Giải pháp**:
1. Kiểm tra file CSV có đủ cột
2. Không được để trống trường required
3. Re-map fields trong Import wizard

### Lỗi: "Foreign key not found"
**Nguyên nhân**: Import sai thứ tự

**Giải pháp**:
1. Import Phòng ban trước
2. Sau đó import Nhân viên
3. Đảm bảo references tồn tại

### Lỗi: "Encoding problem"
**Nguyên nhân**: File không phải UTF-8

**Giải pháp**:
1. Mở file CSV bằng Notepad++
2. Encoding → Convert to UTF-8
3. Save và import lại

---

## 💡 TIPS

### Tip 1: Backup trước khi import
```bash
pg_dump -U odoo -d your_db > backup.sql
```

### Tip 2: Test với 1 record trước
- Tạo file CSV chỉ 1 dòng
- Import thử
- Nếu OK → Import full

### Tip 3: Sử dụng Excel để tạo CSV
- Dễ chỉnh sửa hơn
- Save As → CSV (UTF-8)

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Xem `TROUBLESHOOTING.md`
2. Check logs: Menu → Settings → Technical → Logging
3. Contact: support@company.com

---

**Happy importing!** 🚀

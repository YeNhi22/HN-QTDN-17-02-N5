# Hướng dẫn xóa dữ liệu, import Excel và testcase từng chức năng

**Dự án:** HN-QTDN-17-02-N5 | **Odoo:** 15 | **Port:** 8069

---

## 1. Code có chạy được trên Odoo không?

**Có.** Toàn bộ 4 module custom chạy trên **Odoo 15**:

| Module | Chức năng |
|--------|-----------|
| `nhan_su` | HRM — nguồn dữ liệu gốc |
| `quan_ly_tai_san` | Quản lý tài sản, mượn trả, đề xuất mua |
| `quan_ly_tai_chinh` | Phê duyệt mua, khấu hao, báo cáo TC |
| `q_trang_chu` | Dashboard + AI Chatbot |

**Điều kiện chạy ổn định:**

```bash
cd /mnt/e/HN-QTDN-17-02-N5
python3 odoo-bin.py -c odoo.conf -u nhan_su,quan_ly_tai_san,quan_ly_tai_chinh,q_trang_chu
```

**Lưu ý:** Module tài chính cần **Chart of Accounts** (bảng cân đối kế toán Việt Nam). Nếu phê duyệt mua báo lỗi bút toán → vào **Kế toán → Cấu hình → Cài đặt** → bật kế toán và import COA.

---

## 2. Import dữ liệu từ Excel được không?

**Có — với dữ liệu nền (master data).** Odoo hỗ trợ import trực tiếp file **`.csv`**, **`.xlsx`**, **`.xls`**.

| Loại dữ liệu | Import Excel? | Ghi chú |
|--------------|---------------|---------|
| Phòng ban, Chức vụ, Nhân viên | ✅ Có | File có sẵn |
| Lịch sử công tác | ✅ Có | Import sau nhân viên |
| Danh mục / Tài sản / Phân bổ | ✅ Có | File có sẵn |
| Đơn mượn, Phê duyệt mua, Báo cáo | ❌ Không | Tạo qua UI khi testcase (luồng nghiệp vụ) |

**File dữ liệu có sẵn trong repo:**

```
docs/import_data/
├── Import_DuLieu_Test.xlsx     ← Mở bằng Excel (7 sheet)
├── 01_phong_ban.csv            ← Hoặc import từng file CSV
├── 02_chuc_vu.csv
├── 03_nhan_vien.csv
├── 04_lich_su_cong_tac.csv
├── 05_danh_muc_tai_san.csv
├── 06_tai_san.csv
└── 07_phan_bo_tai_san.csv
```

Tạo lại file Excel (nếu cần):

```bash
cd docs/import_data
pip install openpyxl
python generate_excel.py
```

---

## 3. Xóa toàn bộ dữ liệu cũ (2 cách)

> **Tại sao vẫn thấy NV001–NV007?**  
> Đó là **dữ liệu demo tự load** từ file `qlns_demo.xml` khi cài module `nhan_su`.  
> Trước đây file này nằm trong mục `data` → **mỗi lần cài/update module là nó quay lại**.  
> Code đã sửa: demo chỉ load khi tạo DB có tick "Demo data". **Bạn vẫn phải xóa 1 lần** bằng cách dưới đây.

### Cách A — Tạo database mới (khuyến nghị, sạch nhất)

1. Mở http://localhost:8069/web/database/manager (pass: `admin123`)
2. **Drop** database cũ (ví dụ `quan_ly_btl`)
3. **Create Database** mới:
   - Tên: `quan_ly_btl`
   - Language: Vietnamese
   - **Bỏ tick Demo data**
4. Cài module theo thứ tự: `nhan_su` → `quan_ly_tai_san` → `quan_ly_tai_chinh` → `q_trang_chu`
5. Chạy script xóa demo (module tự load dữ liệu mẫu XML — bước 3.2)

### Cách B — Giữ database, xóa dữ liệu nghiệp vụ

```bash
cd /mnt/e/HN-QTDN-17-02-N5
python3 odoo-bin.py shell -c odoo.conf -d quan_ly_btl < docs/scripts/purge_business_data.py
```

Script xóa: nhân sự, tài sản, mượn trả, phê duyệt, báo cáo… **Không xóa** user admin, cấu hình Odoo, chart of accounts.

### Cách C — Xóa nhanh trên giao diện Odoo (không cần terminal)

**Bật Developer mode** trước (Settings → Activate the developer mode).

Xóa **đúng thứ tự** (con trước, cha sau):

| STT | Menu | Thao tác |
|-----|------|----------|
| 1 | QLTS → Đơn mượn / Quản lý mượn trả | Chọn tất cả → Action → Delete |
| 2 | QLTS → Đề xuất mua / QLTC → Phê duyệt | Xóa hết |
| 3 | QLTS → Phân bổ tài sản | Chọn tất cả → Delete |
| 4 | QLTS → Tài sản | Chọn tất cả → Delete |
| 5 | QLTS → Loại tài sản | Chọn tất cả → Delete |
| 6 | QLNS → **Lịch sử công tác** | Chọn tất cả → Delete |
| 7 | QLNS → **Quản lý nhân viên** | Tick ô đầu bảng → Delete (xóa NV001–NV007) |
| 8 | QLNS → Quản lý phòng ban / chức vụ | Xóa hết |

Sau khi xóa xong, danh sách Nhân viên phải **trống** → mới import Excel/CSV mới.

---

## 4. Import dữ liệu từ Excel/CSV (bắt buộc đúng thứ tự)

> ⚠️ **Phải import đúng thứ tự** vì có liên kết Many2one (`/id`).

### Bước 4.1 — Mở Developer Mode

**Settings → Activate the developer mode** (hoặc thêm `?debug=1` vào URL).

### Bước 4.2 — Import từng bảng

Với **mỗi sheet/file**, làm như sau:

1. Vào menu tương ứng → chế độ **List** (danh sách)
2. **Favorites (★) → Import records**
3. Upload file CSV tương ứng **HOẶC** export sheet từ `Import_DuLieu_Test.xlsx` ra CSV rồi import
4. Odoo map cột → bấm **Test** → **Import**
5. Tick **Use first row as header**

| STT | Menu Odoo | File import | Số dòng |
|-----|-----------|-------------|---------|
| 1 | QLNS → Quản lý phòng ban | `01_phong_ban.csv` | 4 |
| 2 | QLNS → Quản lý chức vụ | `02_chuc_vu.csv` | 4 |
| 3 | QLNS → Quản lý nhân viên | `03_nhan_vien.csv` | 4 |
| 4 | QLNS → Lịch sử công tác * | `04_lich_su_cong_tac.csv` | 4 |
| 5 | QLTS → Loại tài sản | `05_danh_muc_tai_san.csv` | 4 |
| 6 | QLTS → Quản lý tài sản cụ thể | `06_tai_san.csv` | 5 |
| 7 | QLTS → Phân bổ tài sản | `07_phan_bo_tai_san.csv` | 5 |

\* *Lịch sử công tác:* vào menu **QLNS → Quản lý nhân viên → (menu con nếu có)** hoặc tìm model `lich_su_cong_tac` qua **Settings → Technical → Database Structure → Models** → search `lich_su_cong_tac` → bấm **Records**.

### Bước 4.3 — Kiểm tra sau import

| Kiểm tra | Kỳ vọng |
|----------|---------|
| NV001 Nguyễn Văn An | Phòng ban hiện tại = **IT**, Chức vụ = **Trưởng phòng** |
| NV003 Lê Minh Cường | Phòng ban hiện tại = **KT** |
| TS001 | Có phân bổ cho NV001, phòng IT |
| Phân bổ TS004 | Router ở phòng IT (dùng để test mượn) |

---

## 5. Testcase từng chức năng

Ghi **PASS / FAIL** vào cột Kết quả. Nếu FAIL, chụp màn hình + log lỗi gửi lại để fix.

---

### TC-01 | Mức 1 — HRM: Phòng ban tự tính từ lịch sử công tác

| Bước | Thao tác | Kết quả mong đợi | ✓ |
|------|----------|------------------|---|
| 1 | QLNS → Nhân viên → mở **NV002 Trần Thị Bình** | Phòng ban hiện tại = **IT** | |
| 2 | Tab Lịch sử công tác | 1 dòng: IT / Nhân viên / 2023–2026 | |
| 3 | Sửa time_end = hôm qua → Lưu | Phòng ban hiện tại có thể đổi (hết hiệu lực) | |
| 4 | Khôi phục time_end = 2026-12-31 | Phòng ban = IT trở lại | |

---

### TC-02 | Mức 1 — Phân bổ TS: Phòng ban tự điền từ HRM

| Bước | Thao tác | Kết quả mong đợi | ✓ |
|------|----------|------------------|---|
| 1 | QLTS → Phân bổ tài sản → **Tạo** | Form trống | |
| 2 | Chọn Tài sản **TS005**, Nhân viên **NV004** | Phòng ban **tự điền = KD** | |
| 3 | Lưu (hoặc hủy nếu đã có pb005) | Không lỗi | |

---

### TC-03 | Mức 2 — Luồng mượn trả end-to-end

| Bước | Thao tác | Kết quả mong đợi | ✓ |
|------|----------|------------------|---|
| 1 | QLTS → **Đơn mượn tài sản** → Tạo | | |
| 2 | Tên: `Test mượn router`; PB cho mượn: **IT**; NV mượn: **NV004 Phạm Thu Dung**; TG mượn/trả hợp lệ; Lý do: test | | |
| 3 | **Lưu** → Tab tài sản → thêm **Router TS004** | | |
| 4 | **Lưu** → **📤 Gửi duyệt** | Trạng thái = Chờ duyệt; message có mã phiếu | |
| 5 | QLTS → **Quản lý mượn trả** → mở phiếu mới | Trạng thái Chờ duyệt, có TS004 | |
| 6 | **✅ Duyệt cho mượn** | Đơn mượn = Đã duyệt | |
| 7 | **📦 Xác nhận đã giao tài sản** | Trạng thái Đang mượn; phân bổ TS004 = đang mượn | |
| 8 | **✅ Xác nhận đã nhận trả** → chọn tình trạng **Tốt** | Phiếu = Đã trả; Đơn mượn = Đã trả; TS004 = Bình thường | |

---

### TC-04 | Mức 2 — Đề xuất mua → Phê duyệt tự động

| Bước | Thao tác | Kết quả mong đợi | ✓ |
|------|----------|------------------|---|
| 1 | QLTS → **Đề xuất mua tài sản** → Tạo | | |
| 2 | Tiêu đề: `Mua laptop NV mới`; Lý do: test; Phòng ban tự điền **IT** | | |
| 3 | Tab chi tiết: Laptop Dell Inspiron; Danh mục **PC**; SL=1; Giá=22000000; KH tuyến tính 5 năm | | |
| 4 | **Gửi đề xuất** | Trạng thái Chờ phê duyệt TC | |
| 5 | QLTC → **Phê duyệt mua tài sản** → mở đơn mới | Trạng thái Nháp/Chờ duyệt | |
| 6 | Chọn **TK tài sản**, **TK nguồn vốn**, **Sổ nhật ký** (từ COA) | | |
| 7 | **Phê duyệt** | Tạo tài sản mới + phân bổ phòng IT + bút toán (nếu COA OK) | |
| 8 | QLTS → Tài sản | Có tài sản mới mã PD-... | |

---

### TC-05 | Mức 2 — Báo cáo tài chính + khấu hao

| Bước | Thao tác | Kết quả mong đợi | ✓ |
|------|----------|------------------|---|
| 1 | QLTC → Báo cáo tài chính → Tạo | Tháng/Năm hiện tại | |
| 2 | Nhập doanh thu, các loại chi phí | | |
| 3 | **Tính toán & Đồng bộ Khấu hao** | Chi phí KH tự điền từ tài sản | |
| 4 | **Hoàn thành** | Báo cáo lưu OK | |

---

### TC-06 | Mức 1 — Kiểm kê tài sản

| Bước | Thao tác | Kết quả mong đợi | ✓ |
|------|----------|------------------|---|
| 1 | QLTS → Kiểm kê tài sản → Tạo | | |
| 2 | Phòng ban **IT**, NV kiểm kê **NV001** | | |
| 3 | Thêm dòng: TS001, SL sổ=1, SL thực=1, TT=Tốt | Lưu OK | |

---

### TC-07 | Mức 3 — Dashboard Trang chủ

| Bước | Thao tác | Kết quả mong đợi | ✓ |
|------|----------|------------------|---|
| 1 | Menu **🏠 Trang chủ** → Dashboard | Hiện số TS, đơn chờ duyệt | |
| 2 | Số **Đang mượn** | Khớp số đơn trạng thái `dang_muon` | |
| 3 | Nút mở Đơn mượn / Phê duyệt | Mở đúng menu | |

---

### TC-08 | Mức 3 — AI Chatbot

| Bước | Thao tác | Kết quả mong đợi | ✓ |
|------|----------|------------------|---|
| 1 | Trang chủ → **🤖 AI Chatbot** (hoặc icon góc màn hình) | Mở được giao diện chat | |
| 2 | Hỏi: `Quy trình mượn tài sản là gì?` | Trả lời có các bước mượn trả | |
| 3 | Hỏi: `Có bao nhiêu tài sản trong hệ thống?` | Số gần đúng với DB (≥5 sau import) | |

*Chatbot AI (Gemini): cần biến môi trường `GEMINI_API_KEY`. Không có key vẫn trả lời rule-based.*

---

## 6. Xử lý lỗi import thường gặp

| Lỗi | Nguyên nhân | Cách sửa |
|-----|-------------|----------|
| `Mã tài sản đã tồn tại` | Demo XML + import trùng mã | Xóa dữ liệu (mục 3) rồi import lại |
| `External ID not found` | Import sai thứ tự | Import lại file phụ thuộc trước (VD: phòng ban trước NV) |
| Cột `/id` không map | Thiếu cột `id` | Dùng đúng file CSV có cột `id` |
| NV không có phòng ban | Chưa import lịch sử công tác | Import file `04_lich_su_cong_tac.csv` |
| Phê duyệt lỗi bút toán | Chưa có COA | Cài Chart of Accounts Việt Nam |

---

## 7. Khi gặp lỗi — gửi lại cho mình

Copy và gửi các thông tin sau:

1. **Testcase số** (VD: TC-03 bước 7)
2. **Ảnh màn hình** lỗi
3. **Log terminal** (dòng ERROR/Traceback):

```bash
python3 odoo-bin.py -c odoo.conf 2>&1 | grep -E "ERROR|Traceback"
```

4. Database đang dùng (`quan_ly_btl` hay tên khác)

---

## 8. Tóm tắt quy trình nhanh

```
1. Drop DB cũ → Tạo DB mới (không demo Odoo)
2. Cài 4 module custom
3. python3 odoo-bin.py shell ... < docs/scripts/purge_business_data.py
4. Import 7 file CSV theo thứ tự (hoặc từng sheet Excel)
5. Chạy TC-01 → TC-08, ghi PASS/FAIL
6. Lỗi → gửi lại để fix tiếp
```

---

*Cập nhật: 27/06/2026 | HN-QTDN-17-02-N5*

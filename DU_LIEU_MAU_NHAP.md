# 📋 DỮ LIỆU MẪU ĐỂ NHẬP VÀO HỆ THỐNG

**Nhập theo đúng thứ tự từ trên xuống**

---

## BƯỚC 1 — NHÂN SỰ

### 1.1 Phòng ban
*(Menu → QLNS → Quản lý phòng ban → Tạo)*

| Mã | Tên phòng ban |
|----|--------------|
| IT | Phòng Công nghệ thông tin |
| KT | Phòng Kế toán |
| HCNS | Phòng Hành chính - Nhân sự |
| KD | Phòng Kinh doanh |

---

### 1.2 Chức vụ
*(Menu → QLNS → Quản lý chức vụ → Tạo)*

| Mã | Tên chức vụ |
|----|------------|
| GD | Giám đốc |
| TP | Trưởng phòng |
| NV | Nhân viên |
| KTV | Kế toán viên |

---

### 1.3 Nhân viên
*(Menu → QLNS → Quản lý nhân viên → Tạo)*

**Nhân viên 1:**
```
Mã định danh : NV001
Họ tên       : Nguyễn Văn An
Ngày sinh    : 15/03/1990
Quê quán     : Hà Nội
Email        : an.nguyen@company.com
Số điện thoại: 0912345678

→ Tab Lịch sử công tác → Thêm dòng:
  Phòng ban         : IT
  Chức vụ           : Trưởng phòng
  Thời gian bắt đầu : 01/01/2023
  Thời gian kết thúc: 31/12/2026
```

**Nhân viên 2:**
```
Mã định danh : NV002
Họ tên       : Trần Thị Bình
Ngày sinh    : 22/07/1995
Email        : binh.tran@company.com
Số điện thoại: 0987654321

→ Tab Lịch sử công tác:
  Phòng ban         : IT
  Chức vụ           : Nhân viên
  Thời gian bắt đầu : 01/03/2023
  Thời gian kết thúc: 31/12/2026
```

**Nhân viên 3:**
```
Mã định danh : NV003
Họ tên       : Lê Minh Cường
Email        : cuong.le@company.com
Số điện thoại: 0901234567

→ Tab Lịch sử công tác:
  Phòng ban         : KT
  Chức vụ           : Kế toán viên
  Thời gian bắt đầu : 01/01/2023
  Thời gian kết thúc: 31/12/2026
```

---

## BƯỚC 2 — TÀI SẢN

### 2.1 Loại tài sản (Danh mục)
*(Menu → Quản lý tài sản → Tài sản → Loại tài sản → Tạo)*

| Mã | Tên loại |
|----|----------|
| PC | Máy tính & Laptop |
| OFFICE | Thiết bị văn phòng |
| NETWORK | Thiết bị mạng |
| PHONE | Điện thoại & Tablet |

---

### 2.2 Tài sản
*(Menu → Quản lý tài sản → Tài sản → Quản lý tài sản cụ thể → Tạo)*

**Tài sản 1 — Laptop Dell:**
```
Mã tài sản        : TS001
Tên tài sản       : Laptop Dell Latitude 5520
Ngày mua          : 01/01/2024
Loại tài sản      : Máy tính & Laptop
Giá trị ban đầu   : 25,000,000
Giá trị hiện tại  : 25,000,000
Đơn vị tiền tệ    : VNĐ
Phương pháp KH    : Tuyến tính
Thời gian SD tối đa: 5 (năm)
Đơn vị tính       : Chiếc
Ghi chú           : Laptop cho phòng IT
```

**Tài sản 2 — Laptop HP:**
```
Mã tài sản        : TS002
Tên tài sản       : Laptop HP ProBook 450
Ngày mua          : 01/03/2024
Loại tài sản      : Máy tính & Laptop
Giá trị ban đầu   : 20,000,000
Giá trị hiện tại  : 20,000,000
Phương pháp KH    : Tuyến tính
Thời gian SD tối đa: 5
Đơn vị tính       : Chiếc
```

**Tài sản 3 — Máy in:**
```
Mã tài sản        : TS003
Tên tài sản       : Máy in Canon LBP2900
Ngày mua          : 15/02/2024
Loại tài sản      : Thiết bị văn phòng
Giá trị ban đầu   : 5,500,000
Giá trị hiện tại  : 5,500,000
Phương pháp KH    : Tuyến tính
Thời gian SD tối đa: 7
Đơn vị tính       : Chiếc
```

**Tài sản 4 — Router WiFi:**
```
Mã tài sản        : TS004
Tên tài sản       : Router WiFi TP-Link Archer
Ngày mua          : 01/01/2024
Loại tài sản      : Thiết bị mạng
Giá trị ban đầu   : 3,200,000
Giá trị hiện tại  : 3,200,000
Phương pháp KH    : Tuyến tính
Thời gian SD tối đa: 7
```

**Tài sản 5 — Điện thoại:**
```
Mã tài sản        : TS005
Tên tài sản       : iPhone 14 Pro
Ngày mua          : 01/06/2024
Loại tài sản      : Điện thoại & Tablet
Giá trị ban đầu   : 28,000,000
Giá trị hiện tại  : 28,000,000
Phương pháp KH    : Tuyến tính
Thời gian SD tối đa: 3
```

---

### 2.3 Phân bổ tài sản
*(Menu → Quản lý tài sản → Tài sản → Phân bổ tài sản → Tạo)*

**Phân bổ 1:**
```
Tài sản       : Laptop Dell Latitude 5520 (TS001)
Phòng ban     : IT
Nhân viên     : Nguyễn Văn An  ← chọn NV → phòng ban tự điền
Ngày phân bổ  : 05/01/2024
Trạng thái    : Đang sử dụng
Tình trạng    : Bình thường
Ghi chú       : Cấp cho Trưởng phòng IT
```

**Phân bổ 2:**
```
Tài sản       : Laptop HP ProBook 450 (TS002)
Phòng ban     : IT
Nhân viên     : Trần Thị Bình
Ngày phân bổ  : 10/03/2024
Trạng thái    : Đang sử dụng
Tình trạng    : Bình thường
```

**Phân bổ 3:**
```
Tài sản       : Máy in Canon (TS003)
Phòng ban     : KT
Nhân viên     : Lê Minh Cường
Ngày phân bổ  : 20/02/2024
Trạng thái    : Đang sử dụng
Tình trạng    : Bình thường
Ghi chú       : Máy in phòng Kế toán
```

---

## BƯỚC 3 — MƯỢN TÀI SẢN

### 3.1 Tạo Đơn mượn
*(Menu → Quản lý tài sản → Mượn trả tài sản → Đơn mượn tài sản → Tạo)*

```
Tên đơn mượn         : Mượn laptop làm báo cáo tháng 6
Phòng ban cho mượn   : IT          ← CHỌN TRƯỚC
Nhân viên mượn       : Nguyễn Văn An
Thời gian mượn       : 19/06/2026 08:00:00
Thời gian trả dự kiến: 26/06/2026 17:00:00
Lý do mượn          : Cần laptop để làm báo cáo dự án tháng 6

→ Lưu trước
→ Tab "Danh sách tài sản mượn" → Thêm dòng:
  Tài sản           : Laptop Dell Latitude (TS001)
  Tình trạng trước  : Tốt
  Ghi chú           : Mượn tạm 1 tuần

→ Lưu → Bấm [📤 Gửi duyệt]
```

---

### 3.2 Duyệt tại Quản lý mượn trả
*(Menu → Quản lý tài sản → Mượn trả tài sản → Quản lý mượn trả tài sản)*

```
→ Tìm phiếu vừa tạo (trạng thái: Chờ duyệt)
→ Mở → Bấm [✅ Duyệt cho mượn]
→ Bấm [📦 Xác nhận đã giao tài sản]
```

---

## BƯỚC 4 — ĐỀ XUẤT MUA TÀI SẢN

*(Menu → Quản lý tài sản → Đề xuất mua tài sản → Tạo)*

```
Tiêu đề đề xuất     : Mua máy tính cho nhân viên mới
Ngày đề xuất        : 19/06/2026
Phòng ban           : IT
Lý do đề xuất       : Phòng IT có 2 nhân viên mới cần laptop làm việc.
                      Laptop hiện tại đã 5 năm tuổi, hiệu suất thấp.
Đơn vị tiền tệ      : VNĐ

→ Tab Chi tiết thiết bị → Thêm dòng:
  Tên thiết bị      : Laptop Dell Inspiron 15
  Danh mục TS       : Máy tính & Laptop  ← BẮT BUỘC
  Mô tả             : Core i7, RAM 16GB, SSD 512GB
  Thông số KT       : Intel Core i7-1255U, 16GB DDR4, 512GB NVMe
  Số lượng          : 2
  Đơn vị tính       : Chiếc
  Đơn giá           : 22,000,000
  PP khấu hao       : Khấu hao tuyến tính
  Thời gian SD      : 5 (năm)
  Nhà cung cấp      : Dell Vietnam

→ Lưu → Bấm [Gửi đề xuất]
```

→ Sau khi gửi: vào **Quản lý tài chính → Phê duyệt mua tài sản** để duyệt.

---

## BƯỚC 5 — PHÊ DUYỆT MUA (Module Tài chính)

*(Menu → Quản lý tài chính → Phê duyệt mua tài sản)*

```
→ Mở đơn vừa tạo (trạng thái: Chờ phê duyệt)
→ Điền tài khoản kế toán:
  TK Tài sản  : chọn bất kỳ tài khoản có sẵn
  TK Nguồn vốn: chọn bất kỳ tài khoản có sẵn
  Sổ nhật ký  : chọn sổ có sẵn

→ Bấm [Phê duyệt]
```

Sau khi duyệt:
- ✅ Tự động tạo 2 tài sản Laptop trong module Tài sản
- ✅ Tự động tạo bút toán kế toán
- ✅ Tự động tạo lịch khấu hao

---

## BƯỚC 6 — BÁO CÁO TÀI CHÍNH

*(Menu → Quản lý tài chính → Báo cáo tài chính → Tạo)*

```
Tên báo cáo  : Báo cáo tháng 6/2026
Tháng        : 6
Năm          : 2026
Phòng ban    : IT (tùy chọn, để lọc theo phòng ban)
Doanh thu    : 500,000,000

Chi phí:
  Chi phí lương      : 150,000,000
  Chi phí văn phòng  : 20,000,000
  Chi phí điện nước  : 5,000,000
  Chi phí marketing  : 30,000,000
  Chi phí khác       : 10,000,000

→ Bấm [⚡ Tính toán & Đồng bộ Khấu hao]
   → Chi phí khấu hao tự động điền từ tài sản
→ Bấm [Hoàn thành]
```

---

## BƯỚC 7 — KIỂM KÊ TÀI SẢN

*(Menu → Quản lý tài sản → Khấu hao/Kiểm kê → Kiểm kê tài sản → Tạo)*

```
Mã phiếu     : KKTS-00001 (tự sinh)
Tên phiếu    : Kiểm kê tài sản phòng IT tháng 6
Phòng ban    : IT          ← CHỌN TRƯỚC để thấy tài sản
Nhân viên    : Nguyễn Văn An
Thời gian    : 19/06/2026

→ Tab Danh sách kiểm kê → Thêm từng tài sản:
  Tài sản           : Laptop Dell (TS001)
  SL sổ sách        : 1
  SL thực tế        : 1
  Tình trạng        : Tốt
  Trạng thái        : Đã kiểm kê

→ Lưu
```

---

## 🔑 LƯU Ý QUAN TRỌNG

1. **Phân bổ tài sản trước** khi tạo Đơn mượn
   → Tài sản chưa phân bổ sẽ không xuất hiện để chọn

2. **Chọn Phòng ban trước** khi thêm tài sản vào đơn mượn
   → Hệ thống chỉ hiện tài sản của phòng ban đó

3. **Lưu đơn trước** khi thêm dòng tài sản
   → Tránh lỗi "Mã đơn mượn đã tồn tại"

4. **Danh mục tài sản bắt buộc** trong Đề xuất mua
   → Không có danh mục → không gửi được

5. **Thứ tự cài modules**:
   nhan_su → quan_ly_tai_san → quan_ly_tai_chinh → q_trang_chu

---

*File gợi ý nhập liệu | HN-QTDN-17-02-N5 | 19/06/2026*

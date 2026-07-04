# 🥈 DEMO MỨC 2 — TỰ ĐỘNG HÓA

**Tiêu chí**: Hành động của người dùng kích hoạt chuỗi xử lý tự động — không cần làm thêm bước nào.

---

## 3 LUỒNG TỰ ĐỘNG CẦN CHỨNG MINH

| Luồng | Kích hoạt | Kết quả tự động |
|-------|-----------|----------------|
| **Luồng 1** | Phê duyệt mua tài sản | Tạo TS + Bút toán + Lịch KH + KT quản trị |
| **Luồng 2** | Gửi đơn mượn | Tạo phiếu mượn trả tự động |
| **Luồng 3** | Bấm Tính toán báo cáo TC | Đồng bộ chi phí khấu hao tự động |

---

## LUỒNG 1 — ĐỀ XUẤT MUA → PHÊ DUYỆT → TỰ ĐỘNG TẠO TÀI SẢN

### Bước 1.1: Tạo Đề xuất mua tài sản
**Menu → Quản lý tài sản → Đề xuất mua tài sản → Tạo**

```
Tiêu đề đề xuất  : Mua laptop cho nhân viên mới
Ngày đề xuất     : (hôm nay)
Phòng ban        : IT
Lý do đề xuất    : Phòng IT có 2 nhân viên mới cần laptop làm việc.
Đơn vị tiền tệ   : VNĐ
```

→ Tab **Chi tiết thiết bị** → Thêm dòng:
```
Tên thiết bị      : Laptop Dell Inspiron 15
Danh mục TS       : Máy tính & Laptop   ← BẮT BUỘC phải chọn
Số lượng          : 2
Đơn vị tính       : Chiếc
Đơn giá           : 22,000,000
PP khấu hao       : Khấu hao tuyến tính
Thời gian SD      : 5
```

→ **Lưu** → Bấm **[Gửi đề xuất]**

👉 Trạng thái chuyển: **Nháp → Chờ phê duyệt tài chính**  
👉 **Tự động tạo Đơn phê duyệt** ở module Tài chính.

---

### Bước 1.2: Phê duyệt tại module Tài chính
**Menu → Quản lý tài chính → Phê duyệt mua tài sản**

→ Mở đơn vừa tạo (trạng thái: Chờ phê duyệt)

> Hệ thống tự điền TK kế toán 211/112. Nếu chưa có → hệ thống tự tạo.

→ Bấm **[Phê duyệt]**

👉 **Ngay sau khi bấm**, hệ thống TỰ ĐỘNG thực hiện **4 bước**:

**✅ Bước a** — Tạo 2 tài sản Laptop trong module Tài sản  
→ Kiểm tra: **Menu → Quản lý tài sản → Tài sản → Quản lý tài sản cụ thể**  
→ Thấy 2 tài sản mới với ghi chú "Mua từ phê duyệt: PD-xxxxx"

**✅ Bước b** — Tạo bút toán kế toán Nợ 211 / Có 112  
→ Kiểm tra: **Menu → Quản lý tài chính → Kế toán → Bút toán**  
→ Thấy bút toán mới tương ứng

**✅ Bước c** — Tạo lịch khấu hao  
→ Kiểm tra: **Menu → Quản lý tài chính → Khấu hao → Khấu hao tài sản**  
→ Thấy bản ghi khấu hao cho 2 tài sản mới

**✅ Bước d** — Ghi nhận kế toán quản trị  
→ Kiểm tra: **Menu → Quản lý tài chính → Kế toán → Tài khoản quản trị**

---

## LUỒNG 2 — ĐƠN MƯỢN → GỬI DUYỆT → TỰ ĐỘNG TẠO PHIẾU

### Bước 2.1: Tạo Đơn mượn tài sản
**Menu → Quản lý tài sản → Mượn trả tài sản → Đơn mượn tài sản → Tạo**

```
Tên đơn mượn         : Mượn laptop họp dự án
Phòng ban cho mượn   : IT     ← chọn trước
Nhân viên mượn       : Nguyễn Văn An
Thời gian mượn       : (hôm nay) 08:00
Thời gian trả dự kiến: (7 ngày sau) 17:00
Lý do mượn           : Cần laptop để demo dự án cho khách hàng
```

→ **Lưu** trước → Tab **Danh sách tài sản mượn** → Thêm dòng:
```
Tài sản           : Laptop Dell Latitude (TS001)
Tình trạng trước  : Tốt
```

→ **Lưu** → Bấm **[📤 Gửi duyệt]**

👉 Trạng thái: **Nháp → Chờ duyệt**  
👉 **Tự động tạo Phiếu mượn trả** ở màn hình Quản lý mượn trả.

---

### Bước 2.2: Duyệt tại Quản lý mượn trả
**Menu → Quản lý tài sản → Mượn trả tài sản → Quản lý mượn trả tài sản**

→ Tìm phiếu vừa tạo → Mở → Bấm **[✅ Duyệt cho mượn]**  
→ Bấm **[📦 Xác nhận đã giao tài sản]**

👉 Trạng thái tài sản tự cập nhật: **Bình thường → Đang mượn**

---

## LUỒNG 3 — BÁO CÁO TÀI CHÍNH → TÍNH TOÁN → TỰ ĐỘNG ĐỒNG BỘ KH

**Menu → Quản lý tài chính → Báo cáo tài chính → Tạo**

```
Tên báo cáo  : Báo cáo tháng 7/2026
Tháng / Năm  : 7 / 2026
Phòng ban    : IT
Doanh thu    : 600,000,000
Chi phí lương: 150,000,000
Chi phí VP   : 20,000,000
Chi phí điện : 5,000,000
```

→ **Lưu** → Bấm **[⚡ Tính toán & Đồng bộ Khấu hao]**

👉 **Trường "Chi phí khấu hao" tự động điền** — lấy từ lịch sử khấu hao tài sản phòng IT  
👉 **Lợi nhuận và Tỷ lệ lợi nhuận tự tính**  
→ Không cần nhập tay chi phí khấu hao

---

## BẢNG TỔNG KẾT MỨC 2

| Luồng | Thao tác người dùng | Hệ thống tự động làm |
|-------|---------------------|---------------------|
| Mua TS | Bấm [Phê duyệt] 1 lần | Tạo TS + Bút toán + KH + KT quản trị |
| Mượn TS | Bấm [Gửi duyệt] | Tạo phiếu mượn trả |
| Báo cáo TC | Bấm [Tính toán] | Đồng bộ chi phí KH từ module TS |

---

*Demo Mức 2 | HN-QTDN-17-02-N5 | Odoo 15*

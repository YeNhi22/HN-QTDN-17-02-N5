# 📖 HƯỚNG DẪN SỬ DỤNG HỆ THỐNG ERP

**Phiên bản**: 2.0 Premium UI  
**Odoo**: 15.0  
**Ngày cập nhật**: 19/06/2026

---

## 📋 MỤC LỤC

1. [Cài đặt & Khởi động](#1-cài-đặt--khởi-động)
2. [Module Nhân sự (HRM)](#2-module-nhân-sự-hrm)
3. [Module Tài sản](#3-module-tài-sản)
4. [Module Tài chính](#4-module-tài-chính)
5. [Dashboard & AI Chatbot](#5-dashboard--ai-chatbot)
6. [Dữ liệu Test](#6-dữ-liệu-test)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. CÀI ĐẶT & KHỞI ĐỘNG

### 🚀 Bước 1: Khởi động Odoo

```bash
# Cách 1: Development mode
python odoo-bin -c odoo.conf -d your_database --dev=all

# Cách 2: Production mode
python odoo-bin -c odoo.conf -d your_database
```

### 📦 Bước 2: Cài đặt Modules

**THỨ TỰ QUAN TRỌNG** (không được đảo ngược):

```
1. nhan_su           ← CÀI ĐẦU TIÊN (base cho tất cả)
2. quan_ly_tai_san   ← CÀI THỨ 2 (phụ thuộc nhan_su)
3. quan_ly_tai_chinh ← CÀI THỨ 3 (phụ thuộc tài sản)
4. q_trang_chu       ← CÀI CUỐI (dashboard tổng hợp)
```

**Cách cài:**

- Menu → Apps → Update Apps List
- Tìm "nhan_su" → Install
- Tìm "quan_ly_tai_san" → Install
- Tìm "quan_ly_tai_chinh" → Install
- Tìm "q_trang_chu" → Install

### ✅ Kiểm tra cài đặt

Sau khi cài xong, menu sẽ hiện:
- 👥 **Nhân sự** (HRM)
- 📦 **Tài sản** (Assets)
- 💰 **Tài chính** (Finance)
- 🏠 **Trang chủ** (Dashboard)

---

## 2. MODULE NHÂN SỰ (HRM)

### 📊 Chức năng

1. **Quản lý Phòng ban**
2. **Quản lý Chức vụ**
3. **Quản lý Nhân viên**
4. **Lịch sử công tác**

---

### 2.1. PHÒNG BAN

**Truy cập**: Menu → Nhân sự → Cấu hình → Phòng ban

#### 🎯 Hướng dẫn tạo Phòng ban

**Bước 1**: Click nút **Tạo** (màu tím gradient)

**Bước 2**: Điền thông tin:

| Field | Mô tả | Ví dụ |
|-------|-------|-------|
| **Tên phòng ban** | Tên đầy đủ | Phòng Công nghệ thông tin |
| **Mã phòng ban** | Mã viết tắt (unique) | IT |
| **Mô tả** | Chức năng phòng ban | Quản lý hạ tầng IT, phát triển phần mềm |

**Bước 3**: Click **Lưu**

#### 📋 Dữ liệu test Phòng ban

```
Phòng ban 1:
  Tên: Phòng Công nghệ thông tin
  Mã: IT
  Mô tả: Quản lý hạ tầng công nghệ, phát triển phần mềm nội bộ

Phòng ban 2:
  Tên: Phòng Kế toán
  Mã: KT
  Mô tả: Quản lý tài chính, kế toán tổng hợp, thuế

Phòng ban 3:
  Tên: Phòng Hành chính - Nhân sự
  Mã: HCNS
  Mô tả: Quản lý nhân sự, tuyển dụng, văn phòng phẩm

Phòng ban 4:
  Tên: Phòng Kinh doanh
  Mã: KD
  Mô tả: Phát triển thị trường, chăm sóc khách hàng

Phòng ban 5:
  Tên: Phòng Marketing
  Mã: MKT
  Mô tả: Truyền thông, quảng cáo, branding
```

#### 🎨 UI Features

- ✅ **Glassmorphism card** - Form trong suốt với hiệu ứng kính mờ
- ✅ **Gradient button** - Nút Lưu có gradient tím
- ✅ **Smooth animations** - Card hiện ra với animation slideInUp
- ✅ **Hover effects** - Card nâng lên khi hover

---

### 2.2. CHỨC VỤ

**Truy cập**: Menu → Nhân sự → Cấu hình → Chức vụ

#### 🎯 Hướng dẫn tạo Chức vụ


**Bước 1**: Click **Tạo**

**Bước 2**: Điền thông tin:

| Field | Mô tả | Ví dụ |
|-------|-------|-------|
| **Tên chức vụ** | Tên đầy đủ | Lập trình viên |
| **Mã chức vụ** | Mã viết tắt | DEV |
| **Mô tả** | Nhiệm vụ chính | Phát triển và bảo trì hệ thống |

#### 📋 Dữ liệu test Chức vụ

```
Chức vụ 1:
  Tên: Giám đốc
  Mã: GD
  Mô tả: Điều hành toàn bộ hoạt động công ty

Chức vụ 2:
  Tên: Trưởng phòng
  Mã: TP
  Mô tả: Quản lý phòng ban, báo cáo Giám đốc

Chức vụ 3:
  Tên: Lập trình viên
  Mã: DEV
  Mô tả: Phát triển và bảo trì phần mềm

Chức vụ 4:
  Tên: Kế toán viên
  Mã: KTV
  Mô tả: Ghi sổ kế toán, lập báo cáo tài chính

Chức vụ 5:
  Tên: Nhân viên kinh doanh
  Mã: NVKD
  Mô tả: Tìm kiếm và chăm sóc khách hàng

Chức vụ 6:
  Tên: Nhân viên hành chính
  Mã: NVHC
  Mô tả: Quản lý văn phòng, hỗ trợ hành chính
```

---

### 2.3. NHÂN VIÊN

**Truy cập**: Menu → Nhân sự → Nhân viên

#### 🎯 Hướng dẫn tạo Nhân viên


**Bước 1**: Click **Tạo**

**Bước 2**: Điền **Tab Thông tin chung**:

| Field | Bắt buộc | Mô tả |
|-------|----------|-------|
| **Họ và tên** | ✅ | Nguyễn Văn A |
| **Mã nhân viên** | ✅ | NV001 |
| **Email** | ⬜ | nguyenvana@company.com |
| **Số điện thoại** | ⬜ | 0912345678 |
| **Ngày sinh** | ⬜ | 15/03/1995 |
| **Giới tính** | ⬜ | Nam/Nữ/Khác |
| **CMND/CCCD** | ⬜ | 001234567890 |
| **Địa chỉ thường trú** | ⬜ | 123 Đường ABC, Q.1, TP.HCM |

**Bước 3**: Tab **Lịch sử công tác**:

Click **Thêm dòng**:
- **Phòng ban**: IT
- **Chức vụ**: Lập trình viên
- **Ngày bắt đầu**: 01/01/2024
- **Ngày kết thúc**: Để trống (đang làm)

**Bước 4**: Click **Lưu**

#### 📋 Dữ liệu test Nhân viên (10 người)

```
Nhân viên 1:
  Họ tên: Nguyễn Văn An
  Mã NV: NV001
  Email: nguyenvanan@company.com
  SĐT: 0912345678
  Ngày sinh: 15/03/1990
  Lịch sử công tác:
    - Phòng ban: IT | Chức vụ: Trưởng phòng | Từ: 01/01/2024

Nhân viên 2:
  Họ tên: Trần Thị Bình
  Mã NV: NV002
  Email: tranthibinh@company.com
  SĐT: 0987654321
  Ngày sinh: 22/07/1995
  Lịch sử công tác:
    - Phòng ban: IT | Chức vụ: Lập trình viên | Từ: 01/03/2024


Nhân viên 3:
  Họ tên: Lê Minh Cường
  Mã NV: NV003
  Email: leminhcuong@company.com
  SĐT: 0901234567
  Ngày sinh: 10/11/1992
  Lịch sử công tác:
    - Phòng ban: Kế toán | Chức vụ: Trưởng phòng | Từ: 01/01/2024

Nhân viên 4:
  Họ tên: Phạm Thị Dung
  Mã NV: NV004
  Email: phamthidung@company.com
  SĐT: 0976543210
  Ngày sinh: 05/09/1996
  Lịch sử công tác:
    - Phòng ban: Kế toán | Chức vụ: Kế toán viên | Từ: 01/02/2024

Nhân viên 5:
  Họ tên: Hoàng Văn Em
  Mã NV: NV005
  Email: hoangvanem@company.com
  SĐT: 0965432109
  Ngày sinh: 18/04/1994
  Lịch sử công tác:
    - Phòng ban: HCNS | Chức vụ: Trưởng phòng | Từ: 01/01/2024

Nhân viên 6:
  Họ tên: Đỗ Thị Hoa
  Mã NV: NV006
  Email: dothihoa@company.com
  SĐT: 0912345679
  Ngày sinh: 25/12/1997
  Lịch sử công tác:
    - Phòng ban: HCNS | Chức vụ: Nhân viên hành chính | Từ: 15/03/2024

Nhân viên 7:
  Họ tên: Vũ Minh Khoa
  Mã NV: NV007
  Email: vuminhkhoa@company.com
  SĐT: 0923456789
  Ngày sinh: 30/06/1993
  Lịch sử công tác:
    - Phòng ban: Kinh doanh | Chức vụ: Trưởng phòng | Từ: 01/01/2024


Nhân viên 8:
  Họ tên: Bùi Thị Lan
  Mã NV: NV008
  Email: buithilan@company.com
  SĐT: 0934567890
  Ngày sinh: 12/02/1998
  Lịch sử công tác:
    - Phòng ban: Kinh doanh | Chức vụ: Nhân viên kinh doanh | Từ: 01/04/2024

Nhân viên 9:
  Họ tên: Đặng Văn Nam
  Mã NV: NV009
  Email: dangvannam@company.com
  SĐT: 0945678901
  Ngày sinh: 08/08/1991
  Lịch sử công tác:
    - Phòng ban: Marketing | Chức vụ: Trưởng phòng | Từ: 01/01/2024

Nhân viên 10:
  Họ tên: Ngô Thị Phương
  Mã NV: NV010
  Email: ngothiphuong@company.com
  SĐT: 0956789012
  Ngày sinh: 20/05/1999
  Lịch sử công tác:
    - Phòng ban: Marketing | Chức vụ: Nhân viên marketing | Từ: 01/05/2024
```

#### 🎨 UI Features - Nhân viên

- ✅ **Avatar tròn** với shadow + border trắng
- ✅ **Tabs hiện đại** với gradient khi active
- ✅ **Fields có icons** (email, phone, calendar)
- ✅ **Lịch sử công tác** dạng timeline
- ✅ **Computed fields** hiển thị phòng ban/chức vụ hiện tại

---

## 3. MODULE TÀI SẢN

### 📊 Chức năng

1. **Danh mục tài sản**
2. **Quản lý tài sản**
3. **Phân bổ tài sản**

4. **Mượn trả tài sản**
5. **Kiểm kê tài sản**
6. **Thanh lý tài sản**
7. **Lịch sử khấu hao**

---

### 3.1. DANH MỤC TÀI SẢN

**Truy cập**: Menu → Tài sản → Cấu hình → Danh mục tài sản

#### 🎯 Hướng dẫn tạo Danh mục

**Bước 1**: Click **Tạo**

**Bước 2**: Điền thông tin:

| Field | Mô tả | Ví dụ |
|-------|-------|-------|
| **Tên danh mục** | Tên nhóm tài sản | Máy tính |
| **Mã danh mục** | Mã viết tắt | PC |
| **Phương pháp khấu hao** | Đường thẳng/Số dư giảm dần | Đường thẳng |
| **Thời gian khấu hao (năm)** | Số năm khấu hao | 5 |
| **Mô tả** | Chi tiết | Laptop, Desktop, All-in-one |

#### 📋 Dữ liệu test Danh mục

```
Danh mục 1:
  Tên: Máy tính
  Mã: PC
  Phương pháp: Đường thẳng
  Thời gian: 5 năm
  Mô tả: Laptop, Desktop, Workstation

Danh mục 2:
  Tên: Thiết bị văn phòng
  Mã: OFFICE
  Phương pháp: Đường thẳng
  Thời gian: 7 năm
  Mô tả: Bàn, ghế, tủ, kệ

Danh mục 3:
  Tên: Thiết bị mạng
  Mã: NETWORK
  Phương pháp: Đường thẳng
  Thời gian: 7 năm
  Mô tả: Router, Switch, Firewall


Danh mục 4:
  Tên: Phương tiện vận chuyển
  Mã: VEHICLE
  Phương pháp: Đường thẳng
  Thời gian: 10 năm
  Mô tả: Xe ô tô, xe máy

Danh mục 5:
  Tên: Thiết bị điện tử
  Mã: ELEC
  Phương pháp: Đường thẳng
  Thời gian: 3 năm
  Mô tả: Điện thoại, máy in, máy chiếu
```

---

### 3.2. TÀI SẢN

**Truy cập**: Menu → Tài sản → Tài sản

#### 🎯 Hướng dẫn tạo Tài sản

**Bước 1**: Click **Tạo**

**Bước 2**: Tab **Thông tin chung**:

| Field | Bắt buộc | Mô tả |
|-------|----------|-------|
| **Tên tài sản** | ✅ | Dell Latitude 5520 |
| **Mã tài sản** | ✅ | TS001 |
| **Danh mục** | ✅ | Máy tính |
| **Số serial** | ⬜ | DL5520123456 |
| **Ngày mua** | ✅ | 15/01/2024 |
| **Giá trị ban đầu** | ✅ | 25,000,000 VND |
| **Trạng thái** | ✅ | Chưa phân bổ |

**Bước 3**: Tab **Khấu hao**:
- Tự động tính từ Danh mục
- Có thể xem "Lịch sử khấu hao"

**Bước 4**: Click **Lưu**

#### 📋 Dữ liệu test Tài sản (20 tài sản)

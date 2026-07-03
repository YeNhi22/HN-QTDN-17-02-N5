# 📊 BÁO CÁO NGHIỆP VỤ: TRƯỚC VÀ SAU CẢI THIỆN

**Dự án**: Hệ thống ERP Quản lý Nhân sự – Tài sản – Tài chính  
**Nền tảng**: Odoo 15  
**Nhóm**: HN-QTDN-17-02-N5  
**Ngày cập nhật**: 19/06/2026

---

## MỤC LỤC

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Module Nhân sự (HRM)](#2-module-nhân-sự-hrm)
3. [Module Quản lý Tài sản](#3-module-quản-lý-tài-sản)
4. [Module Quản lý Tài chính](#4-module-quản-lý-tài-chính)
5. [Module Trang chủ & AI Chatbot](#5-module-trang-chủ--ai-chatbot)
6. [Tổng kết nghiệp vụ toàn hệ thống](#6-tổng-kết-nghiệp-vụ-toàn-hệ-thống)

---

## 1. TỔNG QUAN HỆ THỐNG

### Sơ đồ tích hợp 4 modules

```
┌──────────────────────────────────────────────────────────────┐
│                     LUỒNG NGHIỆP VỤ                          │
│                                                              │
│  👥 NHÂN SỰ  ──────►  📦 TÀI SẢN  ──────►  💰 TÀI CHÍNH    │
│     (HRM)            (Assets)             (Finance)          │
│       │                  │                    │              │
│       └──────────────────┴────────────────────┘              │
│                          │                                   │
│                   🏠 TRANG CHỦ                               │
│               (Dashboard + AI Chatbot)                       │
└──────────────────────────────────────────────────────────────┘
```

### Mục tiêu cải thiện

| Mục tiêu | Mô tả |
|----------|-------|
| **Mức 1** | Tích hợp HRM → Tài sản: nhân viên là nguồn dữ liệu gốc |
| **Mức 2** | Tự động hóa luồng Đề xuất → Phê duyệt → Tạo tài sản |
| **Mức 3** | Dashboard tổng hợp real-time + AI Chatbot 24/7 |

---

## 2. MODULE NHÂN SỰ (HRM)

### ❌ Nghiệp vụ CŨ

```
Nhân viên được quản lý độc lập, không kết nối với module khác.

Vấn đề:
- Phòng ban/Chức vụ chỉ lưu trong bảng lich_su_cong_tac
- Module Tài sản muốn biết nhân viên ở phòng ban nào phải:
  1. Query bảng nhan_vien
  2. JOIN bảng lich_su_cong_tac
  3. Lấy bản ghi mới nhất
  → 3 bước, chậm, dễ sai

- Phân bổ tài sản: người dùng phải nhập tay tên phòng ban
  → Có thể nhập sai, trùng lặp dữ liệu
  → Không đồng bộ khi nhân viên chuyển phòng ban

Luồng CŨ:
Tạo nhân viên → Nhập phòng ban thủ công ở nhiều nơi
```

### ✅ Nghiệp vụ MỚI (sau cải thiện)

```
Nhân viên là nguồn dữ liệu gốc (Single Source of Truth).

Cải tiến kỹ thuật:
- Thêm computed fields: phong_ban_hien_tai_id, chuc_vu_hien_tai_id
- Tự động tính từ lich_su_cong_tac bản ghi mới nhất
- store=True → lưu vào DB, các module khác đọc trực tiếp

Luồng MỚI:
Nhân viên cập nhật lịch sử công tác
         ↓ (trigger @api.depends)
phong_ban_hien_tai_id tự động cập nhật
         ↓
Module Tài sản đọc trực tiếp → không cần join, không nhập tay
```

**So sánh chi tiết:**

| Tiêu chí | Trước | Sau |
|----------|-------|-----|
| Lấy phòng ban nhân viên | JOIN 2 bảng thủ công | Đọc 1 field trực tiếp |
| Đồng bộ khi chuyển phòng ban | Phải cập nhật thủ công nhiều nơi | Tự động qua computed field |
| Phân bổ tài sản | Nhập tay phòng ban | Auto-fill từ HRM khi chọn nhân viên |
| Xác thực dữ liệu | Có thể nhập sai tên phòng ban | Dùng Many2one → không sai được |

---

## 3. MODULE QUẢN LÝ TÀI SẢN

### 3.1 Nghiệp vụ Phân bổ tài sản

**❌ Trước:**
```
1. Admin tạo tài sản
2. Admin điền phòng ban thủ công
3. Admin điền tên nhân viên thủ công
→ Hay sai, không đồng bộ với HRM
```

**✅ Sau:**
```
1. Admin tạo tài sản
2. Admin chọn nhân viên sử dụng
3. [TỰ ĐỘNG] Phòng ban điền từ HRM
→ Đồng bộ hoàn toàn, không nhập tay
```

---

### 3.2 Nghiệp vụ Mượn trả tài sản

**❌ Luồng CŨ:**
```
Đơn mượn ──(thủ công)──► Quản lý xem ──(thủ công)──► Giao tài sản
Không có: tracking trạng thái, lịch sử, thông báo quá hạn
```

**✅ Luồng MỚI:**
```
Nhân viên                  Quản lý                     Hệ thống
    │                          │                           │
    ├── Tạo Đơn mượn ─────────►│                           │
    │   (nhan_vien, thời gian,  │                           │
    │    tài sản cần mượn)      │                           │
    │                          │                           │
    │                          ├── Xem danh sách chờ duyệt │
    │                          ├── Duyệt / Từ chối ────────►── Tự động cập nhật
    │                          │   (kèm lý do)                  trạng thái tài sản
    │◄── Thông báo kết quả ─────┤
    │
    │   (Sau khi duyệt)
    ├── Nhận tài sản ──────────►── Cập nhật "đang mượn"
    │
    │   (Khi trả)
    ├── Trả tài sản ──────────►── Ghi nhận tình trạng khi trả
    │   + Ghi chú tình trạng       (Tốt / Hỏng / Mất)
    │                              → Cập nhật tinh_trang tài sản
    │
    └── Dashboard: Xem quá hạn, thống kê mượn theo tháng
```

**Trạng thái đơn mượn (state machine):**
```
Nháp ──► Chờ duyệt ──► Đã duyệt ──► Đang mượn ──► Đã trả
             │                │
             └──► Từ chối     └──► Quá hạn (auto-detect)
```

---

### 3.3 Nghiệp vụ Đề xuất mua tài sản

**❌ Trước:**
```
Quy trình thủ công qua email:
Nhân viên email → Quản lý email → Kế toán email → Mua → Nhập kho
→ Mất 5-10 ngày, không tracking, dễ thất lạc
```

**✅ Sau:**
```
1. [Nhân viên] Tạo Đề xuất mua
   - Nhập danh sách thiết bị cần mua
   - Điền số lượng, đơn giá, thông số kỹ thuật
   - Chọn phương pháp khấu hao

2. [Hệ thống] Tự động gửi sang module Tài chính
   - Tạo Đơn phê duyệt ở module Tài chính
   - Gửi Activity notification cho Quản lý tài chính

3. [Quản lý tài chính] Phê duyệt tại module Tài chính
   - Xem chi tiết đề xuất
   - Điền tài khoản kế toán (Nợ/Có)
   - Phê duyệt → [TỰ ĐỘNG] 4 bước:
     a. Tạo tài sản trong module Tài sản
     b. Tạo bút toán kế toán
     c. Tạo lịch khấu hao
     d. Ghi nhận kế toán quản trị

4. [Nhân viên] Theo dõi trạng thái real-time
```

---

### 3.4 Nghiệp vụ Kiểm kê & Thanh lý

**❌ Trước:**
```
- Kiểm kê: ghi chép tay vào sổ, không có lịch sử
- Thanh lý: chỉ xóa record, không tracking
```

**✅ Sau:**
```
Kiểm kê:
1. Tạo phiếu kiểm kê theo phòng ban
2. Nhân viên kiểm kê quét từng tài sản
3. Ghi nhận tình trạng (Tốt / Hỏng / Mất)
4. Lịch sử kiểm kê lưu đầy đủ trên mỗi tài sản

Thanh lý:
1. Tài sản hết khấu hao → Đề xuất thanh lý
2. Chọn hành động: Bán / Tiêu hủy
3. Ghi nhận giá bán (nếu bán)
4. Trạng thái tài sản → "Đã thanh lý"
5. Không thể thanh lý 2 lần (constraint)
```

---

## 4. MODULE QUẢN LÝ TÀI CHÍNH

### 4.1 Nghiệp vụ Khấu hao tài sản

**❌ Trước:**
```
- Nhập tay số tiền khấu hao mỗi kỳ
- Không liên kết với tài sản thực tế
- Dễ sai, không có lịch sử
```

**✅ Sau:**
```
Hệ thống khấu hao tự động 2 phương pháp:

Phương pháp 1: Đường thẳng (Straight-line)
  Khấu hao hàng năm = Nguyên giá / Thời gian sử dụng
  Ví dụ: Laptop 25tr, dùng 5 năm → 5tr/năm

Phương pháp 2: Số dư giảm dần (Degressive)
  Khấu hao = Giá trị hiện tại × Tỷ lệ khấu hao
  Ví dụ: Laptop 25tr, tỷ lệ 20% → Năm 1: 5tr, Năm 2: 4tr...

Tự động:
- Bấm "Tính khấu hao" → Tạo phiếu khấu hao
- Cập nhật gia_tri_hien_tai trên tài sản
- Lưu lịch sử đầy đủ
```

### 4.2 Nghiệp vụ Báo cáo tài chính

**❌ Trước:**
```
Báo cáo nhập tay:
- Doanh thu, chi phí nhập từng con số
- Chi phí khấu hao tính tay → hay sai
- Không lọc theo phòng ban được
```

**✅ Sau:**
```
Báo cáo tự động:
1. Chọn Tháng/Năm + Phòng ban
2. Bấm "Tính toán & Đồng bộ Khấu hao"
3. [TỰ ĐỘNG]:
   - Lấy chi phí khấu hao từ module Tài sản
   - Lọc theo phòng ban (tích hợp HRM)
   - Tính lợi nhuận = Doanh thu - Tổng chi phí
   - Tính tỷ lệ lợi nhuận

Lợi ích:
- Không nhập tay chi phí khấu hao
- Số liệu chính xác, đồng bộ real-time
- Lọc theo phòng ban được
```

### 4.3 Nghiệp vụ Bút toán kế toán

**❌ Trước:**
```
Ghi bút toán thủ công:
- Nhập Nợ/Có tay
- Dễ nhầm tài khoản
- Không liên kết với nghiệp vụ thực
```

**✅ Sau:**
```
Bút toán tự động khi phê duyệt mua tài sản:
  Nợ: TK Tài sản cố định (VD: TK 211)
  Có: TK Nguồn vốn (VD: TK 331)
  Số tiền: Tổng giá trị thiết bị

Trạng thái: Dự thảo → Vào sổ → Hủy
```

---

## 5. MODULE TRANG CHỦ & AI CHATBOT

### 5.1 Dashboard tổng quan

**❌ Trước:**
```
Không có dashboard → Phải vào từng module để xem
→ Mất thời gian, không có cái nhìn tổng thể
```

**✅ Sau:**
```
Dashboard real-time tích hợp từ tất cả modules:

┌─────────────────────────────────────────┐
│  📊 STATS CARDS (real-time từ DB)       │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │TS:150│ │Chờ:12│ │Mượn:8│ │2.5 tỷ│  │
│  └──────┘ └──────┘ └──────┘ └──────┘  │
│                                         │
│  ⚡ QUICK ACTIONS                       │
│  [Tạo đơn] [Duyệt] [Tài sản] [Mua]    │
│                                         │
│  🔔 Thông báo   │  📜 Hoạt động        │
│  • 12 chờ duyệt │  • Đơn #001 duyệt   │
│  • 3 quá hạn   │  • Đơn #002 tạo mới │
└─────────────────────────────────────────┘

Dữ liệu 100% từ database, không hardcode.
```

### 5.2 AI Chatbot

**❌ Trước:** Không có

**✅ Sau:**
```
AI Chatbot hỗ trợ 24/7:
- Trả lời câu hỏi về quy trình mượn tài sản
- Hướng dẫn thủ tục đề xuất mua
- Cung cấp thông tin về tài sản đang mượn
- Knowledge Base có thể cập nhật
- FAQ & Quy chế quy định
- Lịch sử hội thoại lưu theo user
```

---

## 6. TỔNG KẾT NGHIỆP VỤ TOÀN HỆ THỐNG

### 6.1 Luồng nghiệp vụ tổng thể (sau cải thiện)

```
═══════════════════════════════════════════════════════════════
                    LUỒNG ĐẦY ĐỦ
═══════════════════════════════════════════════════════════════

BƯỚC 1: THIẾT LẬP HRM (Module Nhân sự)
├── Tạo Phòng ban (IT, Kế toán, HCNS, Kinh doanh...)
├── Tạo Chức vụ (GĐ, TP, NV...)
└── Tạo Nhân viên + Lịch sử công tác
    → [AUTO] phong_ban_hien_tai_id cập nhật

BƯỚC 2: NHẬP KHO TÀI SẢN (Module Tài sản)
├── Tạo Danh mục tài sản (Máy tính, Bàn ghế...)
├── Nhập Tài sản (tên, giá trị, khấu hao)
└── Phân bổ cho nhân viên/phòng ban
    → [AUTO] Phòng ban điền từ HRM khi chọn NV

BƯỚC 3: HOẠT ĐỘNG HÀNG NGÀY (Mượn trả)
├── NV tạo Đơn mượn tài sản
├── Quản lý duyệt/từ chối
├── Giao tài sản → Trạng thái "Đang mượn"
└── Trả tài sản → Ghi nhận tình trạng

BƯỚC 4: MUA SẮM (Đề xuất → Phê duyệt)
├── NV tạo Đề xuất mua thiết bị
├── [AUTO] Tạo Đơn phê duyệt ở module Tài chính
├── Quản lý TC phê duyệt
└── [AUTO] Tạo tài sản + bút toán + lịch khấu hao

BƯỚC 5: BÁO CÁO (Tài chính)
├── Chọn kỳ báo cáo + phòng ban
├── [AUTO] Đồng bộ chi phí khấu hao
└── Xem lợi nhuận, tỷ lệ chi phí

BƯỚC 6: KIỂM KÊ ĐỊNH KỲ
├── Tạo phiếu kiểm kê theo phòng ban
├── Nhân viên xác nhận từng tài sản
└── Ghi nhận tình trạng thực tế

BƯỚC 7: THANH LÝ KHI HẾT KHẤU HAO
├── Xem tài sản đã hết khấu hao
├── Chọn Bán hoặc Tiêu hủy
└── Cập nhật trạng thái "Đã thanh lý"

═══════════════════════════════════════════════════════════════
```

### 6.2 Bảng so sánh tổng hợp

| Nghiệp vụ | Trước cải thiện | Sau cải thiện | Cải thiện |
|-----------|----------------|---------------|-----------|
| Đồng bộ phòng ban NV | Thủ công, nhập tay | Auto từ HRM | ✅ Tự động |
| Phân bổ tài sản | Nhập tay phòng ban | Auto-fill từ nhân viên | ✅ Tự động |
| Đơn mượn tài sản | Không có tracking | State machine 6 bước | ✅ Đầy đủ |
| Đề xuất mua → Tài sản | Qua email thủ công | Tự động tạo tài sản | ✅ Tự động |
| Khấu hao | Nhập tay từng kỳ | Auto tính 2 phương pháp | ✅ Tự động |
| Báo cáo tài chính | Nhập số tay | Đồng bộ từ module Tài sản | ✅ Tự động |
| Bút toán kế toán | Ghi tay | Auto khi phê duyệt mua | ✅ Tự động |
| Tổng quan hệ thống | Không có | Dashboard real-time | ✅ Mới |
| Hỗ trợ nhân viên | Không có | AI Chatbot 24/7 | ✅ Mới |

### 6.3 Các lỗi kỹ thuật đã sửa

| Lỗi | Mô tả | Ảnh hưởng | Đã sửa |
|-----|-------|-----------|--------|
| `fields.Date.today()` | Gọi hàm khi load class, ngày luôn sai | CRITICAL | ✅ |
| `fields.Datetime.now()` | Tương tự trên với Datetime | CRITICAL | ✅ |
| `self.env.cr.commit()` thủ công | Vi phạm ACID, mất dữ liệu khi lỗi | CRITICAL | ✅ |
| Duplicate model class | 2 class cùng `_name`, data không nhất quán | HIGH | ✅ |
| `tracking=True` không có `mail.thread` | Crash khi ghi dữ liệu | HIGH | ✅ |
| Field `nguyen_gia` không tồn tại | AttributeError khi query dashboard | HIGH | ✅ |
| `nhan_vien.name` thay vì `ho_ten` | AttributeError khi hiển thị | MEDIUM | ✅ |
| `@api.onchange` gán computed field | `_unknown object` crash | CRITICAL | ✅ |
| Import thứ tự sai trong XML | Module không cài được | HIGH | ✅ |
| `widget="monetary"` sai currency | Crash form view | MEDIUM | ✅ |

### 6.4 Tóm tắt điểm nổi bật

```
┌─────────────────────────────────────────────────────────┐
│                    ĐIỂM NỔI BẬT                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔗 TÍCH HỢP                                           │
│     • HRM → Tài sản: 1 nguồn dữ liệu, không trùng lặp │
│     • Tài sản → Tài chính: tự động ghi nhận            │
│     • Tài chính ← Dashboard: real-time                 │
│                                                         │
│  🤖 TỰ ĐỘNG HÓA                                        │
│     • Auto phòng ban khi chọn nhân viên                │
│     • Auto tạo tài sản khi phê duyệt mua               │
│     • Auto khấu hao 2 phương pháp                      │
│     • Auto báo cáo tài chính                           │
│                                                         │
│  📊 TRACKING & MINH BẠCH                               │
│     • Đơn mượn: 6 trạng thái, có lịch sử              │
│     • Đề xuất mua: tracking end-to-end                 │
│     • Tài sản: lịch sử khấu hao, kiểm kê, luân chuyển │
│                                                         │
│  🔒 ĐẢM BẢO CHẤT LƯỢNG                                │
│     • ACID compliance (không commit thủ công)           │
│     • Validation đầy đủ (constraints)                  │
│     • Single Source of Truth (HRM gốc)                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*Tài liệu được tạo tự động dựa trên phân tích source code thực tế của hệ thống.*  
*Ngày tạo: 19/06/2026 | Version: 2.0 | HN-QTDN-17-02-N5*

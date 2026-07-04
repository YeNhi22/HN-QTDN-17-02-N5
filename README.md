# HN-QTDN-17-02-N5 — Hệ thống ERP Quản lý Nhân sự · Tài sản · Tài chính

**Nền tảng**: Odoo 15  
**Nhóm**: HN-QTDN-17-02-N5 | FIT-DNU  
**Môn học**: Thực tập doanh nghiệp

---

## Tổng quan

Hệ thống ERP nội bộ tích hợp 4 modules tùy chỉnh:

| Module | Chức năng chính |
|--------|----------------|
| `nhan_su` | Quản lý nhân viên, phòng ban, chức vụ, lịch sử công tác |
| `quan_ly_tai_san` | Quản lý tài sản, phân bổ, mượn trả, kiểm kê, thanh lý, đề xuất mua |
| `quan_ly_tai_chinh` | Phê duyệt mua, khấu hao, bút toán, báo cáo tài chính |
| `q_trang_chu` | Dashboard real-time, AI Chatbot, OCR hóa đơn |

**Điểm tích hợp nổi bật:**
- HRM là nguồn dữ liệu gốc (Single Source of Truth) — phòng ban/chức vụ tự đồng bộ sang Tài sản và Tài chính
- Phê duyệt mua tài sản tự động tạo tài sản + bút toán kế toán + lịch khấu hao
- AI Chatbot hỗ trợ 24/7 dựa trên Knowledge Base + dữ liệu thực từ database
- Employee Portal cho nhân viên tự xem tài sản, tạo đơn mượn

---

## Yêu cầu

- Windows 10/11 với WSL2 + Ubuntu 22.04
- Docker Desktop (WSL2 backend)
- Python 3.10

---

## Cài đặt nhanh

### 1. Clone và cài thư viện

```bash
git clone https://github.com/FIT-DNU/Business-Internship.git HN-QTDN-17-02-N5
cd HN-QTDN-17-02-N5

sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev \
  libssl-dev python3.10-dev build-essential libffi-dev zlib1g-dev \
  python3.10-venv libpq-dev

python3.10 -m venv ./venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### 2. Khởi động database

```bash
sudo docker-compose up -d
```

### 3. Chạy Odoo

```bash
python3 odoo-bin.py -c odoo.conf
```

Vào **http://localhost:8069** → tạo database → cài 4 modules theo thứ tự.

> Xem chi tiết: [HUONG_DAN_CHAY.md](HUONG_DAN_CHAY.md)

---

## Chạy hàng ngày

```bash
cd /mnt/d/HN-QTDN-17-02-N5
source venv/bin/activate
python3 odoo-bin.py -c odoo.conf
```

→ Truy cập: **http://localhost:8069**  
→ Đăng nhập: `admin@admin.com` / `admin`

---

## Cấu trúc thư mục

```
HN-QTDN-17-02-N5/
├── addons/
│   ├── nhan_su/              # Module Nhân sự (HRM)
│   ├── quan_ly_tai_san/      # Module Quản lý Tài sản
│   ├── quan_ly_tai_chinh/    # Module Quản lý Tài chính
│   └── q_trang_chu/          # Dashboard + AI Chatbot
├── employee_portal/          # Web app nhân viên (HTML thuần)
├── import_data/              # CSV dữ liệu mẫu để import
├── odoo.conf                 # Cấu hình Odoo (port 8069, DB port 5434)
├── docker-compose.yml        # PostgreSQL 15 + Odoo container
├── requirements.txt          # Python dependencies
│
├── HUONG_DAN_CHAY.md         # Hướng dẫn cài đặt & chạy server
├── HUONG_DAN_SU_DUNG.md      # Hướng dẫn sử dụng từng module
├── DU_LIEU_MAU_NHAP.md       # Dữ liệu mẫu để nhập tay
├── DEMO_MUC_1.md             # Hướng dẫn demo Mức 1 (Tích hợp HRM)
├── DEMO_MUC_2.md             # Hướng dẫn demo Mức 2 (Tự động hóa)
└── DEMO_MUC_3.md             # Hướng dẫn demo Mức 3 (AI & Dashboard)
```

---

## Tài khoản mặc định

| Loại | Tài khoản | Mật khẩu |
|------|-----------|----------|
| Admin Odoo | admin@admin.com | admin |
| DB Manager | — | admin123 |
| Employee Portal | nv001 → nv007 | 123456 |

---

## Demo 3 mức

| Mức | Tính năng | File hướng dẫn |
|-----|-----------|---------------|
| 🥉 Mức 1 | Tích hợp HRM — phòng ban tự đồng bộ | [DEMO_MUC_1.md](DEMO_MUC_1.md) |
| 🥈 Mức 2 | Tự động hóa — phê duyệt mua → tự tạo TS + bút toán | [DEMO_MUC_2.md](DEMO_MUC_2.md) |
| 🥇 Mức 3 | AI Chatbot + Dashboard real-time + OCR | [DEMO_MUC_3.md](DEMO_MUC_3.md) |

---

## Công nghệ sử dụng

- **Backend**: Odoo 15 (Python 3.10, ORM, XML views)
- **Database**: PostgreSQL 15 (Docker)
- **AI**: Groq API (llama-3.3-70b) + Google Gemini 2.0 Flash (fallback)
- **Frontend Portal**: HTML/CSS/JavaScript thuần
- **Infrastructure**: WSL2, Docker Desktop

---

*HN-QTDN-17-02-N5 · FIT-DNU · Odoo 15*

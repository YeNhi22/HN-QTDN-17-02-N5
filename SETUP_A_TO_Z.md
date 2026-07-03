# 🚀 HƯỚNG DẪN CÀI ĐẶT & CHẠY — ODOO 15
### Nhóm 5 | Đề tài 5: Quản lý Tài sản + Tài chính/Kế toán
> **Môi trường:** Windows 10/11 + WSL2 Ubuntu 22.04 + Docker Desktop

---

## 📋 YÊU CẦU TRƯỚC KHI BẮT ĐẦU

| Phần mềm | Trạng thái | Kiểm tra |
|---|---|---|
| WSL2 + Ubuntu 22.04 | Bắt buộc | `wsl -l -v` trong PowerShell |
| Docker Desktop | Bắt buộc | Mở Docker Desktop, bật WSL Integration |
| Python 3.10 | Bắt buộc | `python3.10 --version` trong Ubuntu |
| Git | Bắt buộc | `git --version` |

---

## 🐳 CÁCH 1: CHẠY BẰNG DOCKER (Đơn giản nhất)

> Chỉ cần Docker Desktop đang chạy, không cần cài Python packages

### Lần đầu cài đặt

**Bước 1 – Mở Ubuntu terminal:**
```
Win → gõ "Ubuntu 22.04" → mở
```

**Bước 2 – Vào thư mục project:**
```bash
cd /mnt/d/HN-QTDN-17-02-N5
```

**Bước 3 – Bật Docker WSL Integration:**
```
Docker Desktop → Settings → Resources → WSL Integration
→ Bật Ubuntu-22.04 → Apply & Restart
```

**Bước 4 – Khởi động containers:**
```bash
sudo docker-compose up -d
```

**Bước 5 – Kiểm tra containers đang chạy:**
```bash
sudo docker ps
```
Phải thấy 2 container:
- `odoo_server` – Up
- `postgres_odoo-base-15-04` – Up

**Bước 6 – Mở trình duyệt:**
```
http://localhost:8071
```

**Bước 7 – Tạo database lần đầu:**
```
http://localhost:8071/web/database/manager

Master Password : admin
Database Name   : quan_ly_btl
Email           : admin@admin.com
Password        : admin
Language        : Vietnamese (Tiếng Việt)
Country         : Vietnam
Demo Data       : ☐ BỎ TICK
→ Create Database
```

**Bước 8 – Cài modules theo thứ tự:**
```
Apps → Update Apps List → Update

Cài lần lượt (đợi xong từng cái):
1. nhan_su
2. quan_ly_tai_san
3. quan_ly_tai_chinh
4. q_trang_chu
```

---

### Mỗi lần bật máy (Docker)

```bash
# Mở Ubuntu terminal
cd /mnt/d/HN-QTDN-17-02-N5
sudo docker-compose up -d
```
→ Mở Chrome: **http://localhost:8071**
→ Đăng nhập: `admin@admin.com` / `admin`

---

### Sau khi sửa code (Docker)

```bash
# Update module cụ thể
sudo docker exec odoo_server odoo -c /etc/odoo/odoo.conf \
  -u q_trang_chu -d quan_ly_btl --stop-after-init
sudo docker restart odoo_server

# Hoặc restart nhanh (không update DB)
sudo docker restart odoo_server
```

---

## 🐍 CÁCH 2: CHẠY BẰNG PYTHON THUẦN — PORT 8069

> Docker chỉ chạy PostgreSQL, Odoo chạy thẳng bằng Python

### Lần đầu cài đặt

**Bước 1 – Mở Ubuntu terminal và vào thư mục:**
```bash
cd /mnt/d/HN-QTDN-17-02-N5
```

**Bước 2 – Cài thư viện hệ thống:**
```bash
sudo apt-get update && sudo apt-get install -y \
  libxml2-dev libxslt-dev libldap2-dev libsasl2-dev \
  libssl-dev python3.10-dev build-essential \
  libffi-dev zlib1g-dev python3.10-venv libpq-dev
```

**Bước 3 – Tạo môi trường ảo Python:**
```bash
python3.10 -m venv ./venv
```
> ⚠️ Chỉ chạy 1 lần duy nhất. Lần sau bỏ qua bước này.

**Bước 4 – Kích hoạt môi trường ảo:**
```bash
source venv/bin/activate
```
> Dấu nhắc sẽ thành `(venv) user@...`

**Bước 5 – Cài Python packages:**
```bash
pip3 install -r requirements.txt
```
> ⚠️ Chỉ chạy 1 lần. Lần sau bỏ qua.

**Bước 6 – Chỉ khởi động PostgreSQL (không khởi động Odoo Docker):**
```bash
sudo docker-compose up -d postgres-odoo-base-15-04
```

**Bước 7 – Tạo file odoo.conf:**
```bash
[options]
addons_path = addons
db_host = 127.0.0.1
db_user = odoo
db_password = odoo
db_port = 5434
http_port = 8069
admin_passwd = admin123
log_level = info
```
> ⚠️ Chỉ tạo 1 lần. Lần sau bỏ qua.

**Bước 8 – Chạy Odoo:**
```bash
fuser -k 8069/tcp 2>/dev/null
python3 odoo-bin.py -c odoo.conf
```

Chờ thấy dòng này:
```
INFO odoo.service.server: HTTP service running on 0.0.0.0:8069
```

→ Mở Chrome: **http://localhost:8069**

---

### Mỗi lần bật máy (Python thuần)

```bash
cd /mnt/d/HN-QTDN-17-02-N5
source venv/bin/activate
sudo docker-compose up -d postgres-odoo-base-15-04
fuser -k 8069/tcp 2>/dev/null
python3 odoo-bin.py -c odoo.conf
```

---

### Sau khi sửa code (Python thuần)

```bash
# Ctrl+C để dừng server, rồi:
python3 odoo-bin.py -c odoo.conf \
  -u nhan_su,quan_ly_tai_san,quan_ly_tai_chinh,q_trang_chu
```

---

## ⚙️ CẤU HÌNH GEMINI API (AI Chatbot & OCR)

**Cách 1 – Qua giao diện Odoo (đơn giản):**
```
Thiết lập → Tích hợp AI & Telegram
→ Gemini API Key: [dán key vào đây]
→ Lưu
```

**Cách 2 – Qua file .env (bền vững):**
```bash
# Sửa file .env
nano .env
# Thay YOUR_KEY bằng key thực:
# GEMINI_API_KEY=AQ.Ab8RN6...
```
Sau đó restart Docker:
```bash
sudo docker-compose down
sudo docker-compose up -d
```

> 📌 Key Gemini lấy tại: https://aistudio.google.com/app/apikey
> Key đúng có dạng `AQ.Ab8RN6...` (format mới từ 6/2026)

---

## 🔧 XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi: Port 8069 bị chiếm
```bash
fuser -k 8069/tcp
python3 odoo-bin.py -c odoo.conf
```

### Lỗi: Không kết nối được database
```bash
sudo docker-compose up -d postgres-odoo-base-15-04
# Kiểm tra:
docker exec postgres_odoo-base-15-04 pg_isready
```

### Lỗi: Module không cài được / RPC Error
```bash
# Xem log chi tiết
docker logs odoo_server --tail=50

# Update module bị lỗi
sudo docker exec odoo_server odoo -c /etc/odoo/odoo.conf \
  -u TEN_MODULE -d quan_ly_btl --stop-after-init
```

### Lỗi: Wrong login/password
```bash
# Kiểm tra tên đăng nhập thực trong DB
docker exec postgres_odoo-base-15-04 \
  psql -U odoo -d quan_ly_btl \
  -c "SELECT login FROM res_users WHERE active=true;"
```

### Lỗi: Gemini API 401
- Key sai format → lấy key mới tại https://aistudio.google.com/app/apikey

### Lỗi: Gemini API 429
- Hết quota → chờ đến 7:00 sáng hôm sau (quota reset theo giờ UTC)
- Hoặc dùng key từ tài khoản Google khác

---

## 📊 THÔNG TIN TRUY CẬP

| Mục | Docker (Cách 1) | Python thuần (Cách 2) |
|---|---|---|
| **URL** | http://localhost:8071 | http://localhost:8069 |
| **DB Manager** | http://localhost:8071/web/database/manager | http://localhost:8069/web/database/manager |
| **Email** | admin@admin.com | admin@admin.com |
| **Password** | admin | admin |
| **Database** | quan_ly_btl | quan_ly_btl |

---

## 📦 CÀI MODULES THỨ TỰ BẮT BUỘC

```
1. nhan_su           ← HRM – Dữ liệu gốc, phải cài TRƯỚC
2. quan_ly_tai_san   ← Phụ thuộc nhan_su
3. quan_ly_tai_chinh ← Phụ thuộc quan_ly_tai_san + nhan_su
4. q_trang_chu       ← Dashboard + AI Chatbot + OCR
```

---

## 🗂️ CẤU TRÚC FILE QUAN TRỌNG

```
HN-QTDN-17-02-N5/
├── addons/
│   ├── nhan_su/           # Module HRM
│   ├── quan_ly_tai_san/   # Module Tài sản
│   ├── quan_ly_tai_chinh/ # Module Tài chính
│   └── q_trang_chu/       # Dashboard + AI
├── odoo-docker.conf       # Config cho Docker
├── odoo.conf              # Config cho Python thuần (tự tạo)
├── docker-compose.yml     # Docker containers
├── .env                   # API keys (không commit lên Git)
├── requirements.txt       # Python dependencies
└── odoo-bin.py            # Entry point Odoo
```

---

*Nhóm 5 – Lê Ngọc Minh, Đỗ Khánh Hùng, Nguyễn Quang Trung, Nguyễn Vũ Yến Nhi*
*Odoo 15 | FIT-DNU | 2026*

# 🚀 HƯỚNG DẪN CHẠY HỆ THỐNG — HN-QTDN-17-02-N5

> Gồm 2 phần:
> - **PHẦN 1**: Cài đặt lần đầu trên máy mới (chỉ làm 1 lần)
> - **PHẦN 2**: Chạy hàng ngày (từ bước CD trở đi)

---

# PHẦN 1 — CÀI ĐẶT LẦN ĐẦU TRÊN MÁY MỚI

## Bước 1: Cài WSL2 + Ubuntu 22.04

Mở **PowerShell** (Run as Administrator):

```powershell
wsl --install
```

Restart máy khi được yêu cầu. Sau khi vào lại Windows:

```powershell
wsl --install -d Ubuntu-22.04
```

Khi Ubuntu mở ra → nhập username và password Linux.

Kiểm tra:
```powershell
wsl -l -v
# Kết quả mong muốn: Ubuntu-22.04   Running   2
```

---

## Bước 2: Cài Docker Desktop

1. Tải tại: https://www.docker.com/products/docker-desktop/
2. Cài đặt, chọn **Use WSL 2 backend**
3. Restart Windows
4. Mở Docker Desktop → **Settings → Resources → WSL Integration**  
   → Bật toggle cho **Ubuntu-22.04** → **Apply & Restart**

Kiểm tra trong Ubuntu:
```bash
docker --version
docker run hello-world
```

---

## Bước 3: Clone code về máy

Mở **Ubuntu (WSL)**, clone project vào ổ D:

```bash
cd /mnt/d
git clone https://github.com/FIT-DNU/Business-Internship.git HN-QTDN-17-02-N5
cd HN-QTDN-17-02-N5
```

Mở VS Code (nếu muốn xem/sửa code):
```bash
code .
```

---

## Bước 4: Cài thư viện hệ thống

```bash
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev libssl-dev \
  python3.10-distutils python3.10-dev build-essential libffi-dev zlib1g-dev \
  python3.10-venv libpq-dev
```

---

## Bước 5: Tạo môi trường ảo Python

> ⚠️ Chỉ làm bước này 1 lần. Những lần sau bỏ qua, chuyển thẳng sang **Bước 6**.

```bash
python3.10 -m venv ./venv
```

---

## Bước 6: Kích hoạt môi trường ảo và cài thư viện

```bash
source venv/bin/activate
pip3 install -r requirements.txt
```

Thấy `(venv)` ở đầu dòng là OK.

---

## Bước 7: Khởi động database (Docker)

```bash
sudo docker-compose up -d
```

Kiểm tra container postgres đã chạy:
```bash
docker ps
# Thấy container postgres_odc Running, port 5434
```

---

## Bước 8: Kiểm tra file odoo.conf

File `odoo.conf` đã có sẵn trong project với nội dung:

```ini
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

> Nếu chưa có file này → tạo mới với nội dung trên.

---

## Bước 9: Chạy Odoo lần đầu và tạo database

```bash
python3 odoo-bin.py -c odoo.conf
```

Chờ thấy:
```
INFO ? odoo.service.server: HTTP service (werkzeug) running on ...:8069
```

Mở trình duyệt, vào: **http://localhost:8069/web/database/manager**

Tạo database:
```
Master Password : admin123
Database Name   : quan_ly_btl
Email           : admin@admin.com
Password        : admin
Language        : Vietnamese (Tiếng Việt)
Country         : Vietnam
Demo Data       : ✅ BỎ TICK (không lấy demo)
```

→ Click **Create Database** → chờ 2–3 phút.

---

## Bước 10: Cài modules theo thứ tự

Vào **http://localhost:8069** → đăng nhập `admin@admin.com` / `admin`

```
Menu → Ứng dụng → Update Apps List → Update
```

Cài từng module theo thứ tự:
```
1. Tìm "nhan_su"          → Install → chờ xong
2. Tìm "quan_ly_tai_san"  → Install → chờ xong
3. Tìm "quan_ly_tai_chinh"→ Install → chờ xong
4. Tìm "q_trang_chu"      → Install → chờ xong
```

> ⚠️ Phải cài đúng thứ tự, đợi xong từng module mới cài tiếp.

---

## Bước 11: Update modules sau khi cài (quan trọng)

Dừng server (Ctrl+C), chạy lệnh update để load đầy đủ dữ liệu mẫu:

```bash
python3 odoo-bin.py -c odoo.conf -u nhan_su,quan_ly_tai_san,quan_ly_tai_chinh,q_trang_chu --stop-after-init -d quan_ly_btl
```

Chờ xong → chạy lại server bình thường:
```bash
python3 odoo-bin.py -c odoo.conf
```

✅ Lúc này dữ liệu nhân viên mẫu (NV001–NV007) đã có sẵn, tài khoản web hoạt động.

---

---

# PHẦN 2 — CHẠY HÀNG NGÀY

> Từ lần thứ 2 trở đi, chỉ cần làm các bước này.

## Bước 1: Mở Docker Desktop

Mở Docker Desktop, đảm bảo container **postgres_odc** đang chạy (chấm xanh).

> Nếu container **odoo_server** đang chạy → **Stop nó trước** (nó chiếm port 8069).

---

## Bước 2: Mở Ubuntu (WSL)

Nhấn `Win` → tìm **Ubuntu** → mở.

---

## Bước 3: Vào thư mục project

```bash
cd /mnt/d/HN-QTDN-17-02-N5
```

> Đổi `/mnt/d/` nếu project ở ổ khác (e → `/mnt/e/`, c → `/mnt/c/`).

---

## Bước 4: Kích hoạt môi trường ảo

```bash
source venv/bin/activate
```

---

## Bước 5: Chạy Odoo

```bash
python3 odoo-bin.py -c odoo.conf
```

Chờ thấy dòng `HTTP service (werkzeug) running on ...:8069` → mở trình duyệt.

---

## Bước 6: Vào hệ thống

```
http://localhost:8069
```

Đăng nhập: `admin@admin.com` / `admin`

---

---

# XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi: Port 8069 bị chiếm
```bash
sudo pkill -9 -f "odoo-bin"
sudo fuser -k 8069/tcp 2>/dev/null
python3 odoo-bin.py -c odoo.conf
```

### Lỗi: Connection refused port 5434 (PostgreSQL chưa chạy)
→ Vào Docker Desktop → start container **postgres_odc**

### Lỗi: docker command not found trong WSL
→ Docker Desktop → Settings → Resources → WSL Integration → bật Ubuntu-22.04 → Apply & Restart  
→ Đóng và mở lại terminal Ubuntu

### Sau khi sửa code — update module
```bash
# Dừng server (Ctrl+C), rồi:
python3 odoo-bin.py -c odoo.conf -u nhan_su,quan_ly_tai_san,quan_ly_tai_chinh,q_trang_chu --stop-after-init -d quan_ly_btl
# Chạy lại:
python3 odoo-bin.py -c odoo.conf
```

---

# THÔNG TIN ĐĂNG NHẬP

| | |
|---|---|
| URL hệ thống | http://localhost:8069 |
| Admin | admin@admin.com / admin |
| DB Manager | http://localhost:8069/web/database/manager |
| DB Manager pass | admin123 |
| Employee Portal | http://localhost:8069/portal |
| Portal accounts | nv001 → nv007 / 123456 |

---

*HN-QTDN-17-02-N5 | Odoo 15 | FIT-DNU*

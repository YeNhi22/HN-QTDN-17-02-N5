#!/bin/bash
# Chạy script này sau khi import nhân viên để set tài khoản web
# Dùng: bash setup_web_accounts.sh <tên_database>
# Ví dụ: bash setup_web_accounts.sh quan_ly_btl

DB=${1:-quan_ly_btl}
echo "Setting web accounts for database: $DB"

docker exec postgres_odoo-base-15-04 psql -U odoo -d $DB -c "
UPDATE nhan_vien SET
  web_username = LOWER(ma_dinh_danh),
  web_password_hash = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',
  is_web_active = true
WHERE web_username IS NULL OR web_username = '' OR web_password_hash IS NULL;

SELECT ma_dinh_danh, ho_ten, web_username, is_web_active FROM nhan_vien ORDER BY ma_dinh_danh;
"
echo "Done! Default password: 123456"

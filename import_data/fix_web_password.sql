-- Chạy lệnh này sau khi import nhân viên vào Odoo để set mật khẩu web đúng
-- Mật khẩu mặc định: 123456

UPDATE nhan_vien SET
  web_username = ma_dinh_danh,
  web_password_hash = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',
  is_web_active = true
WHERE ma_dinh_danh IN ('NV001','NV002','NV003','NV004','NV005','NV006','NV007');

-- Kiểm tra kết quả
SELECT ma_dinh_danh, ho_ten, web_username, is_web_active FROM nhan_vien ORDER BY ma_dinh_danh;

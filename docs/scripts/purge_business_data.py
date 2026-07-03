# -*- coding: utf-8 -*-
"""
Xóa toàn bộ dữ liệu nghiệp vụ custom (giữ cấu hình Odoo, user admin, chart of accounts).

Chạy trong Odoo shell:
  cd /mnt/e/HN-QTDN-17-02-N5
  python3 odoo-bin.py shell -c odoo.conf -d TEN_DATABASE < docs/scripts/purge_business_data.py

Hoặc copy-paste nội dung vào shell tương tác.
"""
# Xóa theo thứ tự phụ thuộc (con trước, cha sau)
MODELS_PURGE_ORDER = [
    # Mượn trả
    'don_muon_tai_san_line',
    'muon_tra_tai_san_line',
    'don_muon_tai_san',
    'muon_tra_tai_san',
    # Đề xuất / phê duyệt
    'de_xuat_mua_tai_san.line',
    'de_xuat_mua_tai_san',
    'phe_duyet_mua_tai_san.line',
    'phe_duyet_mua_tai_san',
    # Kiểm kê, luân chuyển, thanh lý
    'kiem_ke_tai_san_line',
    'kiem_ke_tai_san',
    'luan_chuyen_tai_san_line',
    'luan_chuyen_tai_san',
    'thanh_ly_tai_san',
    'lich_su_khau_hao',
    'lich_su_ky_thuat',
    # Tài chính
    'tinh_toan_khau_hao.line',
    'tinh_toan_khau_hao',
    'lich_khau_hao',
    'khau_hao_tai_san',
    'but_toan',
    'bao_cao_tai_chinh',
    'tai_khoan_quan_tri',
    # Tài sản
    'phan_bo_tai_san',
    'tai_san',
    'danh_muc_tai_san',
    # HRM
    'lich_su_cong_tac',
    'nhan_vien',
    'chuc_vu',
    'phong_ban',
    # Chatbot (tùy chọn)
    'chatbot.message',
    'chatbot.conversation',
]

print("=== BẮT ĐẦU XÓA DỮ LIỆU NGHIỆP VỤ ===")
for model_name in MODELS_PURGE_ORDER:
    if model_name not in env:
        print(f"  [SKIP] Model không tồn tại: {model_name}")
        continue
    Model = env[model_name]
    count = Model.search_count([])
    if count:
        Model.search([]).unlink()
        print(f"  [OK] Đã xóa {count} bản ghi: {model_name}")
    else:
        print(f"  [--] Rỗng: {model_name}")

env.cr.commit()
print("=== HOAN TAT — co the import Excel/CSV moi ===")

# -*- coding: utf-8 -*-
"""
Khôi phục dữ liệu demo HRM + Tài sản và sửa tình trạng phân bổ bị kẹt.

Chạy trong Odoo shell (từ thư mục gốc dự án):
  python3 odoo-bin shell -c odoo.conf -d TEN_DATABASE < docs/scripts/restore_demo_data.py

Hoặc copy-paste nội dung vào shell tương tác.
"""
import os
from odoo import fields
from odoo.modules.module import get_module_path


def _load_demo_module(module, xml_path):
    """Nạp file demo XML."""
    from odoo.tools import convert_file
    mod_path = get_module_path(module)
    if not mod_path:
        print(f"  [SKIP] Không tìm thấy module: {module}")
        return
    full_path = os.path.join(mod_path, xml_path)
    if not os.path.isfile(full_path):
        print(f"  [SKIP] Không tìm thấy file: {full_path}")
        return
    convert_file(
        env.cr, module, xml_path, {}, 'init', False, 'data', pathname=full_path,
    )
    print(f"  [OK] Đã nạp: {module}/{xml_path}")


def _count(model):
    return env[model].search_count([]) if model in env else 0


print(f"=== DATABASE: {env.cr.dbname} ===")
print("=== KIỂM TRA DỮ LIỆU HIỆN TẠI ===")
for m in ['phong_ban', 'nhan_vien', 'tai_san', 'phan_bo_tai_san']:
    print(f"  {m}: {_count(m)}")

need_hrm = _count('nhan_vien') == 0
need_ts = _count('tai_san') == 0
force_ts = _count('tai_san') == 0 or _count('phan_bo_tai_san') == 0

if need_hrm:
    print("\n=== NẠP DEMO HRM (nhan_su) ===")
    _load_demo_module('nhan_su', 'data/qlns_demo.xml')
else:
    print("\n[--] HRM đã có dữ liệu — bỏ qua nạp demo HRM")

if force_ts:
    print("\n=== NẠP DEMO TÀI SẢN (quan_ly_tai_san) ===")
    _load_demo_module('quan_ly_tai_san', 'data/tai_san_demo.xml')
else:
    print("\n[--] Tài sản đã có dữ liệu — bỏ qua nạp demo tài sản")

# Sửa phân bổ bị kẹt 'dang_muon' do luồng mượn trả hủy giữa chừng
if 'phan_bo_tai_san' in env:
    stuck = env['phan_bo_tai_san'].search([('tinh_trang', '=', 'dang_muon')])
    busy_ids = []
    if 'muon_tra_tai_san' in env:
        active_phieu = env['muon_tra_tai_san'].search([
            ('trang_thai', 'in', ['dang_muon', 'qua_han']),
        ])
        busy_ids = active_phieu.mapped('muon_tra_line_ids.phan_bo_tai_san_id').ids
    to_fix = stuck.filtered(lambda p: p.id not in busy_ids)
    if to_fix:
        to_fix.write({'tinh_trang': 'binh_thuong'})
        print(f"\n[OK] Đã sửa {len(to_fix)} phân bổ kẹt 'Đang mượn' → 'Bình thường'")
    else:
        print("\n[--] Không có phân bổ kẹt cần sửa")

# Đóng phiếu mượn trả sót (đơn đã hủy nhưng phiếu còn treo)
if 'muon_tra_tai_san' in env and 'don_muon_tai_san' in env:
    orphan = env['muon_tra_tai_san'].search([
        ('trang_thai', 'not in', ['tu_choi', 'da_tra']),
        ('ma_don_muon_id.trang_thai', 'in', ['huy', 'tu_choi']),
    ])
    for phieu in orphan:
        phieu._release_phan_bo_assets()
        phieu.write({
            'trang_thai': 'tu_choi',
            'ly_do_tu_choi': 'Đóng phiếu sót (đơn đã hủy/từ chối)',
        })
    if orphan:
        print(f"[OK] Đã đóng {len(orphan)} phiếu mượn trả sót")

# Đơn "đang mượn" nhưng không còn phiếu (xóa phiếu nhầm)
if 'muon_tra_tai_san' in env and 'don_muon_tai_san' in env:
    ghost_don = env['don_muon_tai_san'].search([('trang_thai', '=', 'dang_muon')])
    ghost_fixed = 0
    for don in ghost_don:
        mt = env['muon_tra_tai_san'].search([
            ('ma_don_muon_id', '=', don.id),
            ('trang_thai', 'in', ['dang_muon', 'qua_han']),
        ], limit=1)
        if mt:
            continue
        for pb in don.don_muon_tai_san_ids.mapped('phan_bo_tai_san_id'):
            if pb and pb.tinh_trang == 'dang_muon':
                pb.write({'tinh_trang': 'binh_thuong'})
        don.write({'trang_thai': 'da_tra', 'ngay_tra_thuc_te': fields.Datetime.now()})
        ghost_fixed += 1
    if ghost_fixed:
        print(f"[OK] Đã sửa {ghost_fixed} đơn 'đang mượn' mồ côi (không còn phiếu)")

# Phiếu đang mượn thiếu dòng — tạo lại từ đơn gốc
if 'muon_tra_tai_san' in env:
    rebuilt = 0
    for phieu in env['muon_tra_tai_san'].search([
        ('trang_thai', 'in', ['dang_muon', 'qua_han']),
        ('muon_tra_line_ids', '=', False),
    ]):
        if phieu.ma_don_muon_id:
            phieu._ensure_muon_tra_lines()
            if phieu.muon_tra_line_ids:
                rebuilt += 1
    if rebuilt:
        print(f"[OK] Đã tạo lại dòng tài sản cho {rebuilt} phiếu mượn trả")

env.cr.commit()
print("\n=== HOÀN TẤT ===")
print(f"  Database: {env.cr.dbname}")
print(f"  phong_ban: {_count('phong_ban')}, nhan_vien: {_count('nhan_vien')}, "
      f"tai_san: {_count('tai_san')}, phan_bo: {_count('phan_bo_tai_san')}")
if _count('tai_san'):
    samples = env['tai_san'].search([], limit=3)
    print("  Mẫu:", ", ".join(samples.mapped('ma_tai_san')))
else:
    print("  ⚠ CẢNH BÁO: vẫn chưa có tài sản — kiểm tra đúng database và chạy -u quan_ly_tai_san -d", env.cr.dbname)

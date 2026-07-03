# -*- coding: utf-8 -*-
"""
Sửa dữ liệu mượn trả bị kẹt: tài sản vẫn "Đang mượn" nhưng không còn phiếu/đơn.

Chạy:
  python3 odoo-bin shell -c odoo.conf -d quan_ly_btl < docs/scripts/fix_stuck_borrowing.py

Script sẽ:
  1. Liệt kê phiếu đang mượn không có dòng tài sản → tạo lại dòng từ đơn gốc hoặc đóng phiếu
  2. Liệt kê đơn "Đang mượn" nhưng không còn phiếu hoạt động → đồng bộ trạng thái
  3. Trả phân bổ kẹt "dang_muon" không còn phiếu mượn hợp lệ
"""
from odoo import fields


def _label(record, field='display_name'):
    return getattr(record, field, str(record.id))


print(f"=== SỬA DỮ LIỆU MƯỢN TRẢ KẸT — DB: {env.cr.dbname} ===")

MuonTra = env['muon_tra_tai_san']
DonMuon = env['don_muon_tai_san']
PhanBo = env['phan_bo_tai_san']

active_states = ['dang_muon', 'qua_han']
active_phieu = MuonTra.search([('trang_thai', 'in', active_states)])
busy_pb_ids = set(active_phieu.mapped('muon_tra_line_ids.phan_bo_tai_san_id').ids)

# --- 1. Phiếu đang mượn nhưng thiếu dòng ---
print("\n--- Phiếu đang mượn thiếu dòng tài sản ---")
fixed_lines = 0
closed_phieu = 0
for phieu in active_phieu:
    if phieu.muon_tra_line_ids:
        continue
    print(f"  • {phieu.ma_phieu_muon_tra} — không có dòng")
    if phieu.ma_don_muon_id and phieu.ma_don_muon_id.don_muon_tai_san_ids:
        phieu._ensure_muon_tra_lines()
        if phieu.muon_tra_line_ids:
            fixed_lines += 1
            print(f"    → Đã tạo lại {len(phieu.muon_tra_line_ids)} dòng từ đơn {_label(phieu.ma_don_muon_id, 'ma_don_muon')}")
            continue
    phieu._release_phan_bo_assets()
    phieu.write({
        'trang_thai': 'da_tra',
        'thoi_gian_tra_thuc_te': fields.Datetime.now(),
        'ghi_chu': (phieu.ghi_chu or '') + '\n[Script] Đóng phiếu sót — không còn dòng tài sản.',
    })
    if phieu.ma_don_muon_id and phieu.ma_don_muon_id.trang_thai == 'dang_muon':
        phieu.ma_don_muon_id.write({
            'trang_thai': 'da_tra',
            'ngay_tra_thuc_te': fields.Datetime.now(),
        })
    closed_phieu += 1
    print("    → Đã đóng phiếu và trả tài sản")

if not fixed_lines and not closed_phieu:
    print("  (Không có phiếu thiếu dòng)")

# --- 2. Đơn đang mượn nhưng không còn phiếu hoạt động ---
print("\n--- Đơn 'Đang mượn' không còn phiếu ---")
ghost_don = DonMuon.search([('trang_thai', '=', 'dang_muon')])
fixed_don = 0
for don in ghost_don:
    mt = MuonTra.search([
        ('ma_don_muon_id', '=', don.id),
        ('trang_thai', 'in', active_states),
    ], limit=1)
    if mt:
        continue
    print(f"  • {don.ma_don_muon} — không còn phiếu đang mượn")
    for pb in don.don_muon_tai_san_ids.mapped('phan_bo_tai_san_id'):
        if pb and pb.tinh_trang == 'dang_muon':
            pb.write({'tinh_trang': 'binh_thuong'})
    don.write({
        'trang_thai': 'da_tra',
        'ngay_tra_thuc_te': fields.Datetime.now(),
    })
    fixed_don += 1
    print("    → Đã trả phân bổ và đóng đơn")

if not fixed_don:
    print("  (Không có đơn mồ côi)")

# --- 3. Phân bổ kẹt không còn phiếu mượn ---
print("\n--- Phân bổ kẹt 'Đang mượn' ---")
stuck = PhanBo.search([('tinh_trang', '=', 'dang_muon')])
to_fix = stuck.filtered(lambda p: p.id not in busy_pb_ids)
if to_fix:
    names = ', '.join(to_fix.mapped('tai_san_id.ma_tai_san')[:10])
    to_fix.write({'tinh_trang': 'binh_thuong'})
    print(f"  → Đã sửa {len(to_fix)} phân bổ: {names}")
else:
    print("  (Không có phân bổ kẹt)")

env.cr.commit()
print("\n=== HOÀN TẤT ===")
print("  Phiếu tạo lại dòng:", fixed_lines)
print("  Phiếu đóng sót:", closed_phieu)
print("  Đơn mồ côi đã sửa:", fixed_don)
print("  Phân bổ kẹt đã sửa:", len(to_fix))

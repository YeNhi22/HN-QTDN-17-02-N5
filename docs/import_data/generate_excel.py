#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tạo file Excel Import_DuLieu_Test.xlsx từ các file CSV trong cùng thư mục."""
import csv
from pathlib import Path

try:
    from openpyxl import Workbook
except ImportError:
    print("Cần cài openpyxl: pip install openpyxl")
    raise

BASE = Path(__file__).resolve().parent
FILES = [
    ("01_PhongBan", "01_phong_ban.csv"),
    ("02_ChucVu", "02_chuc_vu.csv"),
    ("03_NhanVien", "03_nhan_vien.csv"),
    ("04_LichSuCongTac", "04_lich_su_cong_tac.csv"),
    ("05_DanhMucTaiSan", "05_danh_muc_tai_san.csv"),
    ("06_TaiSan", "06_tai_san.csv"),
    ("07_PhanBoTaiSan", "07_phan_bo_tai_san.csv"),
]

wb = Workbook()
wb.remove(wb.active)

for sheet_name, csv_name in FILES:
    csv_path = BASE / csv_name
    ws = wb.create_sheet(title=sheet_name[:31])
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.reader(f):
            ws.append(row)

out = BASE / "Import_DuLieu_Test.xlsx"
wb.save(out)
print("Created:", out)

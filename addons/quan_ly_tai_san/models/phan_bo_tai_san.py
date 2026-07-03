# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# Cải tiến từ phiên bản cũ:
# 1. Sửa bug: default=fields.Date.today() → fields.Date.today (không gọi hàm)
# 2. Thêm @api.onchange('nhan_vien_su_dung_id') để tự điền phòng ban từ HRM
#    → Đây là điểm tích hợp quan trọng nhất: nhân viên = nguồn dữ liệu gốc,
#      phòng ban tự động đồng bộ, không nhập tay.


class PhanBoTaiSan(models.Model):
    _name = 'phan_bo_tai_san'
    _description = 'Bảng chứa thông tin Phân bổ tài sản'
    _rec_name = "tai_san_id"
    # Bỏ tracking=True trên các field vì model này không inherit mail.thread

    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban',
        required=False,
        ondelete='set null',
        help='Phòng ban sử dụng tài sản. Tự động điền từ phòng ban hiện tại của nhân viên (HRM).'
    )
    tai_san_id = fields.Many2one('tai_san', string='Tài sản', required=True, ondelete='cascade')

    # Cải tiến từ phiên bản cũ: Sửa bug default=fields.Date.today() (gọi hàm lúc load class)
    # thành default=fields.Date.today (Odoo gọi hàm lúc tạo record) → ngày luôn đúng.
    ngay_phat = fields.Date(
        'Ngày phân bổ',
        required=True,
        default=fields.Date.today,   # ← ĐÃ SỬA BUG: bỏ ()
    )

    nhan_vien_su_dung_id = fields.Many2one(
        comodel_name='nhan_vien',
        string='Nhân viên sử dụng',
        ondelete='set null',
        help='Nhân viên đang sử dụng tài sản. Khi chọn nhân viên, phòng ban tự động đồng bộ từ HRM.'
    )

    ghi_chu = fields.Char('Ghi chú', default='')
    trang_thai = fields.Selection([
        ('in-use', 'Đang sử dụng'),
        ('not-in-use', 'Không sử dụng')
    ], string='Trạng thái', required=True, default='in-use')

    tinh_trang = fields.Selection([
        ('binh_thuong', 'Bình thường'),
        ('dang_muon', 'Đang mượn'),
        ('hu_hong', 'Hư hỏng'),
        ('mat', 'Mất'),
    ], string='Tình trạng', default='binh_thuong',
       help='Tình trạng vật lý hiện tại của tài sản')

    vi_tri_tai_san_id = fields.Many2one(
        'phong_ban', string='Vị trí tài sản', required=False, ondelete='set null'
    )

    custom_name = fields.Char(compute="_compute_custom_name", store=True, string="Tên hiển thị")

    @api.depends('phong_ban_id', 'tai_san_id')
    def _compute_custom_name(self):
        for record in self:
            phong_ban_code = (
                record.phong_ban_id.ma_phong_ban
                if record.phong_ban_id else (record.tai_san_id.ma_tai_san or 'N/A')
            )
            tai_san_name = record.tai_san_id.ten_tai_san or 'Tài sản không xác định'
            record.custom_name = f"{phong_ban_code} - {tai_san_name}"

    def name_get(self):
        result = []
        for record in self:
            ma = record.tai_san_id.ma_tai_san or ''
            ten = record.tai_san_id.ten_tai_san or record.custom_name or ''
            pb = record.phong_ban_id.ma_phong_ban or ''
            label = f"{ma} — {ten}" if ma else ten
            if pb:
                label = f"[{pb}] {label}"
            result.append((record.id, label))
        return result

    # ================================================================
    # Cải tiến từ phiên bản cũ: Thêm @api.onchange để khi người dùng
    # chọn nhân viên, hệ thống TỰ ĐỘNG điền phòng ban từ dữ liệu HRM.
    # Đây là cơ chế đồng bộ HRM → Tài sản, không yêu cầu nhập tay.
    # ================================================================
    @api.onchange('nhan_vien_su_dung_id')
    def _onchange_nhan_vien_su_dung_id(self):
        """Tự động điền phòng ban từ HRM (Single Source of Truth)."""
        if self.nhan_vien_su_dung_id:
            pb = self.nhan_vien_su_dung_id.phong_ban_hien_tai_id
            if pb:
                self.phong_ban_id = pb
                self.vi_tri_tai_san_id = pb

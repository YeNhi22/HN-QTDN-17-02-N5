# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

class DanhMucTaiSan(models.Model):
    _name = 'danh_muc_tai_san'
    _description = 'Bảng chứa thông tin loại tài sản'
    _rec_name = "ten_danh_muc_ts"
    _order = 'ma_danh_muc_ts asc'
    _sql_constraints = [
        ("ma_danh_muc_ts_unique", "unique(ma_danh_muc_ts)", "Mã loại tài sản đã tồn tại !"),
    ]
    
    ma_danh_muc_ts = fields.Char('Mã loại tài sản', required=True, copy=False, default='New')
    ten_danh_muc_ts = fields.Char('Tên loại tài sản', required=True)
    mo_ta_danh_muc_ts = fields.Char('Mô tả loại tài sản')

    so_luong_tong = fields.Integer(string = 'Số lượng hiện có',compute = "_compute_so_luong_tong", store=True)
    tai_san_ids = fields.One2many('tai_san', 'danh_muc_ts_id', string='Tài sản')

    @api.depends('tai_san_ids')
    def _compute_so_luong_tong(self):
        for record in self:
            record.so_luong_tong = len(record.tai_san_ids)

    @api.model
    def default_get(self, fields_list):
        res = super(DanhMucTaiSan, self).default_get(fields_list)
        if 'ma_danh_muc_ts' in fields_list:
            res['ma_danh_muc_ts'] = self.env['sequence.helper'].get_default_code(
                'danh_muc_tai_san', 'ma_danh_muc_ts', 'danh_muc_tai_san', 'DMTS'
            )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        self.env['sequence.helper'].assign_codes_multi(
            vals_list, 'ma_danh_muc_ts', 'danh_muc_tai_san', 'DMTS', 'danh_muc_tai_san'
        )
        return super(DanhMucTaiSan, self).create(vals_list)
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Bảng chứa thông tin chức vụ'
    _rec_name = 'ten_chuc_vu'
    _inherit = ['sequence.helper']

    _sql_constraints = [
        ('ma_chuc_vu_unique', 'UNIQUE(ma_chuc_vu)',
         'Mã chức vụ đã tồn tại, không được trùng.'),
    ]

    ma_chuc_vu = fields.Char("Mã chức vụ", required=True, copy=False, default='New')
    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)
    lich_su_cong_tac_ids = fields.One2many(
        "lich_su_cong_tac", string="Danh sách lịch sử công tác", inverse_name="chuc_vu_id")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'ma_chuc_vu' in fields_list:
            res['ma_chuc_vu'] = self.env['sequence.helper'].get_default_code(
                'chuc_vu', 'ma_chuc_vu', 'chuc_vu.ma_chuc_vu', 'CV'
            )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        self.env['sequence.helper'].assign_codes_multi(
            vals_list, 'ma_chuc_vu', 'chuc_vu.ma_chuc_vu', 'CV', 'chuc_vu'
        )
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('ma_chuc_vu'):
            code = vals['ma_chuc_vu'].strip()
            self.env['sequence.helper'].check_duplicate_code(
                'chuc_vu', 'ma_chuc_vu', code, exclude_ids=self.ids)
            self.env['sequence.helper'].sync_sequence_from_code(
                code, 'chuc_vu.ma_chuc_vu', 'CV')
        return super().write(vals)

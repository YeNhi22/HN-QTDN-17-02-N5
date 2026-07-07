# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Bảng chứa thông tin phòng ban'
    _rec_name = 'ten_phong_ban'
    _inherit = ['sequence.helper']

    _sql_constraints = [
        ('ma_phong_ban_unique', 'UNIQUE(ma_phong_ban)',
         'Mã phòng ban đã tồn tại, không được trùng.'),
    ]

    ma_phong_ban = fields.Char("Mã phòng ban", required=True, copy=False, default='New')
    ten_phong_ban = fields.Char("Tên phòng ban", required=True)
    name = fields.Char("Tên", compute='_compute_name', store=True, readonly=True)
    lich_su_cong_tac_ids = fields.One2many(
        "lich_su_cong_tac", string="Danh sách lịch sử công tác", inverse_name="phong_ban_id")

    @api.depends('ten_phong_ban')
    def _compute_name(self):
        for record in self:
            record.name = record.ten_phong_ban or ''

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'ma_phong_ban' in fields_list:
            res['ma_phong_ban'] = self.env['sequence.helper'].get_default_code(
                'phong_ban', 'ma_phong_ban', 'phong_ban.ma_phong_ban', 'PB'
            )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        self.env['sequence.helper'].assign_codes_multi(
            vals_list, 'ma_phong_ban', 'phong_ban.ma_phong_ban', 'PB', 'phong_ban'
        )
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('ma_phong_ban'):
            code = vals['ma_phong_ban'].strip()
            self.env['sequence.helper'].check_duplicate_code(
                'phong_ban', 'ma_phong_ban', code, exclude_ids=self.ids)
            self.env['sequence.helper'].sync_sequence_from_code(
                code, 'phong_ban.ma_phong_ban', 'PB')
        return super().write(vals)

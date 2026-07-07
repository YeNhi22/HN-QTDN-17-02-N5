# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LichSuCongTac(models.Model):
    _name = 'lich_su_cong_tac'
    _description = 'Bảng chứa thông tin lịch sử công tác'
    _order = 'time_start desc, id desc'

    time_start = fields.Date(
        "Thời gian bắt đầu", required=True,
        default=lambda self: fields.Date.today())
    time_end = fields.Date(
        "Thời gian kết thúc",
        help='Để trống = đang công tác (chưa kết thúc)')
    phong_ban_id = fields.Many2one("phong_ban", string="Phòng ban", required=True)
    chuc_vu_id = fields.Many2one("chuc_vu", string="Chức vụ", required=True)
    nhan_vien_id = fields.Many2one("nhan_vien", string="Nhân viên", required=True, ondelete='cascade')
    dang_hieu_luc = fields.Boolean(
        string='Đang hiệu lực', compute='_compute_dang_hieu_luc', store=True)

    @api.depends('time_start', 'time_end')
    def _compute_dang_hieu_luc(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.dang_hieu_luc = bool(
                rec.time_start
                and rec.time_start <= today
                and (not rec.time_end or rec.time_end >= today)
            )

    @api.constrains('time_start', 'time_end')
    def _check_dates(self):
        for rec in self:
            if rec.time_end and rec.time_start and rec.time_end < rec.time_start:
                raise ValidationError('Ngày kết thúc không được trước ngày bắt đầu.')

    @api.model
    def _close_previous_active(self, nhan_vien_id, new_start):
        """Đóng các lịch sử đang mở của nhân viên trước khi thêm/chuyển mới."""
        if not nhan_vien_id or not new_start:
            return
        new_start_date = fields.Date.to_date(new_start)
        open_lines = self.search([
            ('nhan_vien_id', '=', nhan_vien_id),
            '|', ('time_end', '=', False), ('time_end', '>=', new_start_date),
        ])
        for line in open_lines:
            end_date = new_start_date
            if line.time_start and line.time_start >= new_start_date:
                end_date = line.time_start
            line.write({'time_end': end_date})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            nv_id = vals.get('nhan_vien_id')
            start = vals.get('time_start') or fields.Date.today()
            vals.setdefault('time_start', start)
            if nv_id:
                self._close_previous_active(nv_id, start)
            if not vals.get('time_end'):
                vals['time_end'] = False
        records = super().create(vals_list)
        records._trigger_hrm_sync()
        return records

    def write(self, vals):
        old_employee_state = {}
        for rec in self:
            if rec.nhan_vien_id:
                nv = rec.nhan_vien_id
                old_employee_state[nv.id] = (
                    nv.phong_ban_hien_tai_id,
                    nv.chuc_vu_hien_tai_id,
                )

        if any(k in vals for k in ('phong_ban_id', 'chuc_vu_id', 'time_start', 'time_end')):
            for rec in self:
                nv_id = vals.get('nhan_vien_id', rec.nhan_vien_id.id)
                new_start = vals.get('time_start', rec.time_start)
                if nv_id and new_start:
                    new_start_date = fields.Date.to_date(new_start)
                    others = self.search([
                        ('nhan_vien_id', '=', nv_id),
                        ('id', '!=', rec.id),
                        '|', ('time_end', '=', False), ('time_end', '>=', new_start_date),
                    ])
                    for other in others:
                        other.write({'time_end': new_start_date})

        res = super().write(vals)

        affected_nv_ids = set()
        for rec in self:
            if rec.nhan_vien_id:
                affected_nv_ids.add(rec.nhan_vien_id.id)

        for nv_id in affected_nv_ids:
            nv = self.env['nhan_vien'].browse(nv_id)
            old_pb, old_cv = old_employee_state.get(nv_id, (False, False))
            new_pb = nv.phong_ban_hien_tai_id
            new_cv = nv.chuc_vu_hien_tai_id
            if old_pb != new_pb or old_cv != new_cv:
                self.env['hrm.sync.log'].log_department_change(
                    nv, old_pb, new_pb, old_cv, new_cv)
                self.env['system.event'].safe_emit(
                    'hrm.department_changed',
                    f'HRM: {nv.ho_ten} chuyển phòng ban',
                    source_model='nhan_vien',
                    source_id=nv.id,
                    payload={
                        'nhan_vien': nv.ho_ten,
                        'phong_ban_cu': old_pb.ten_phong_ban if old_pb else '—',
                        'phong_ban_moi': new_pb.ten_phong_ban if new_pb else '—',
                    },
                )
        return res

    def _trigger_hrm_sync(self):
        for rec in self:
            if rec.nhan_vien_id:
                pb = rec.nhan_vien_id.phong_ban_hien_tai_id
                cv = rec.nhan_vien_id.chuc_vu_hien_tai_id
                self.env['hrm.sync.log'].log_department_change(
                    rec.nhan_vien_id, False, pb, False, cv)

# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrmSyncLog(models.Model):
    """Nhật ký đồng bộ dữ liệu HRM → các module khác (Mức 1)."""
    _name = 'hrm.sync.log'
    _description = 'Nhật ký đồng bộ HRM'
    _order = 'create_date desc'

    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên', ondelete='set null')
    phong_ban_cu_id = fields.Many2one('phong_ban', string='Phòng ban cũ', ondelete='set null')
    phong_ban_moi_id = fields.Many2one('phong_ban', string='Phòng ban mới', ondelete='set null')
    chuc_vu_cu_id = fields.Many2one('chuc_vu', string='Chức vụ cũ', ondelete='set null')
    chuc_vu_moi_id = fields.Many2one('chuc_vu', string='Chức vụ mới', ondelete='set null')
    module_dich = fields.Char(string='Module đích', help='Module nhận dữ liệu đồng bộ')
    mo_ta = fields.Text(string='Mô tả')
    trang_thai = fields.Selection([
        ('thanh_cong', 'Thành công'),
        ('canh_bao', 'Cảnh báo'),
        ('loi', 'Lỗi'),
    ], string='Trạng thái', default='thanh_cong', required=True)

    @api.model
    def log_department_change(self, nhan_vien, old_pb, new_pb, old_cv=None, new_cv=None):
        """Ghi log khi phòng ban/chức vụ nhân viên thay đổi."""
        if not nhan_vien:
            return self.env['hrm.sync.log']

        mo_ta_parts = [
            f'HRM cập nhật nhân viên [{nhan_vien.ma_dinh_danh}] {nhan_vien.ho_ten}.',
        ]
        if old_pb != new_pb:
            mo_ta_parts.append(
                f'Phòng ban: {old_pb.ten_phong_ban if old_pb else "—"} → '
                f'{new_pb.ten_phong_ban if new_pb else "—"}.'
            )
        if old_cv != new_cv:
            mo_ta_parts.append(
                f'Chức vụ: {old_cv.ten_chuc_vu if old_cv else "—"} → '
                f'{new_cv.ten_chuc_vu if new_cv else "—"}.'
            )
        mo_ta_parts.append(
            'Các module Tài sản/Tài chính đọc phong_ban_hien_tai_id trực tiếp từ HRM.'
        )

        return self.sudo().create({
            'nhan_vien_id': nhan_vien.id,
            'phong_ban_cu_id': old_pb.id if old_pb else False,
            'phong_ban_moi_id': new_pb.id if new_pb else False,
            'chuc_vu_cu_id': old_cv.id if old_cv else False,
            'chuc_vu_moi_id': new_cv.id if new_cv else False,
            'module_dich': 'Tài sản, Tài chính',
            'mo_ta': '\n'.join(mo_ta_parts),
            'trang_thai': 'thanh_cong',
        })

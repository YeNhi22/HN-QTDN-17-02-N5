# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DeXuatMuaTaiSan(models.Model):
    """Model đề xuất mua tài sản - Bước 1 trong luồng mua thiết bị"""
    _name = 'de_xuat_mua_tai_san'
    _description = 'Đề xuất mua tài sản'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ma_de_xuat'
    _order = 'ngay_de_xuat desc'

    # ============ THÔNG TIN CƠ BẢN ============
    ma_de_xuat = fields.Char(
        string='Mã đề xuất', required=True, readonly=True,
        copy=False, default='New', tracking=True,
    )
    ten_de_xuat = fields.Char(string='Tiêu đề đề xuất', required=True, tracking=True)
    ngay_de_xuat = fields.Date(
        string='Ngày đề xuất', default=fields.Date.context_today,
        required=True, tracking=True,
    )
    nguoi_de_xuat_id = fields.Many2one(
        'res.users', string='Người đề xuất',
        default=lambda self: self.env.user, tracking=True, ondelete='set null',
    )
    nhan_vien_id = fields.Many2one(
        'nhan_vien', string='Nhân viên đề xuất (HRM)',
        tracking=True, ondelete='set null',
        help='Dữ liệu gốc từ module HRM — phòng ban tự động đồng bộ.',
    )
    phong_ban_id = fields.Many2one(
        'phong_ban', string='Phòng ban',
        ondelete='set null', tracking=True,
    )

    # ============ CHI TIẾT ============
    line_ids = fields.One2many(
        'de_xuat_mua_tai_san.line', 'de_xuat_id', string='Chi tiết thiết bị',
    )
    tong_gia_tri = fields.Float(
        string='Tổng giá trị', compute='_compute_tong_gia_tri', store=True, tracking=True,
    )
    don_vi_tien_te = fields.Selection(
        [('vnd', 'VNĐ'), ('usd', 'USD')],
        string='Đơn vị tiền tệ', default='vnd', required=True,
    )
    ly_do = fields.Text(string='Lý do đề xuất', required=True, tracking=True)
    mo_ta = fields.Html(string='Mô tả chi tiết')
    dinh_kem_ids = fields.Many2many('ir.attachment', string='File đính kèm')
    ngay_du_kien_nhan = fields.Date(string='Ngày dự kiến nhận hàng')
    ghi_chu = fields.Text(string='Ghi chú')

    # ============ TRẠNG THÁI ============
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Đã gửi'),
        ('waiting_approval', 'Chờ phê duyệt tài chính'),
        ('approved', 'Đã phê duyệt'),
        ('rejected', 'Từ chối'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', required=True, tracking=True)

    # ============ LIÊN KẾT ============
    phe_duyet_id = fields.Many2one(
        'phe_duyet_mua_tai_san', string='Đơn phê duyệt',
        readonly=True, tracking=True, ondelete='set null',
    )
    tai_san_ids = fields.Many2many('tai_san', string='Tài sản đã tạo', readonly=True)
    tai_san_count = fields.Integer(string='Số lượng tài sản', compute='_compute_tai_san_count')

    # ============ COMPUTE ============
    @api.depends('tai_san_ids')
    def _compute_tai_san_count(self):
        for r in self:
            r.tai_san_count = len(r.tai_san_ids)

    @api.depends('line_ids.thanh_tien')
    def _compute_tong_gia_tri(self):
        for r in self:
            r.tong_gia_tri = sum(r.line_ids.mapped('thanh_tien'))

    # ============ CRUD ============
    @api.model
    def create(self, vals):
        if vals.get('ma_de_xuat', 'New') == 'New':
            vals['ma_de_xuat'] = (
                self.env['ir.sequence'].next_by_code('de_xuat_mua_tai_san') or 'New'
            )
        if not vals.get('phong_ban_id') and vals.get('nguoi_de_xuat_id'):
            nv = self._resolve_nhan_vien_from_user(vals.get('nguoi_de_xuat_id'))
            if nv:
                vals['nhan_vien_id'] = nv.id
                if nv.phong_ban_hien_tai_id:
                    vals['phong_ban_id'] = nv.phong_ban_hien_tai_id.id
        if vals.get('nhan_vien_id') and not vals.get('phong_ban_id'):
            nv = self.env['nhan_vien'].browse(vals['nhan_vien_id'])
            if nv.phong_ban_hien_tai_id:
                vals['phong_ban_id'] = nv.phong_ban_hien_tai_id.id
        return super().create(vals)

    @api.model
    def _resolve_nhan_vien_from_user(self, user_id):
        if not user_id:
            return self.env['nhan_vien']
        return self.env['nhan_vien'].search([('user_id', '=', user_id)], limit=1)

    @api.onchange('nguoi_de_xuat_id')
    def _onchange_nguoi_de_xuat_id(self):
        """Tự động điền nhân viên và phòng ban từ HRM (Single Source of Truth)."""
        if self.nguoi_de_xuat_id:
            nv = self._resolve_nhan_vien_from_user(self.nguoi_de_xuat_id.id)
            if nv:
                self.nhan_vien_id = nv
                if nv.phong_ban_hien_tai_id:
                    self.phong_ban_id = nv.phong_ban_hien_tai_id

    @api.onchange('nhan_vien_id')
    def _onchange_nhan_vien_id(self):
        """Chọn nhân viên HRM → đồng bộ phòng ban và user Odoo."""
        if self.nhan_vien_id:
            if self.nhan_vien_id.phong_ban_hien_tai_id:
                self.phong_ban_id = self.nhan_vien_id.phong_ban_hien_tai_id
            if self.nhan_vien_id.user_id:
                self.nguoi_de_xuat_id = self.nhan_vien_id.user_id

    def write(self, vals):
        """Ngăn thay đổi state sang approved/rejected trực tiếp"""
        if 'state' in vals and vals['state'] in ['approved', 'rejected']:
            if not self.env.context.get('from_finance_approval') \
               and not self.env.context.get('force_reset'):
                raise UserError(_(
                    'Đề xuất chỉ có thể được phê duyệt thông qua module Quản lý Tài chính.'
                ))
        return super().write(vals)

    # ============ ACTIONS ============
    def action_submit(self):
        """Gửi đề xuất và tạo đơn phê duyệt ở module tài chính"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Chỉ có thể gửi đề xuất ở trạng thái Nháp!'))
            if record.phe_duyet_id:
                raise UserError(_('Đề xuất đã có đơn phê duyệt liên kết!'))
            if not record.line_ids:
                raise UserError(_('Vui lòng thêm ít nhất một thiết bị.'))
            for line in record.line_ids:
                if not line.danh_muc_ts_id:
                    raise UserError(_(
                        'Vui lòng chọn danh mục cho thiết bị: %s'
                    ) % (line.ten_thiet_bi or ''))
            if record.tong_gia_tri <= 0:
                raise UserError(_('Tổng giá trị phải lớn hơn 0.'))

            if not record.phong_ban_id and record.nguoi_de_xuat_id:
                nv = self.env['nhan_vien'].search([
                    ('user_id', '=', record.nguoi_de_xuat_id.id),
                ], limit=1)
                if nv and nv.phong_ban_hien_tai_id:
                    record.phong_ban_id = nv.phong_ban_hien_tai_id

            record._create_approval_request()
            record.state = 'waiting_approval'
            record.message_post(body=_('Đề xuất đã được gửi và tạo đơn phê duyệt tài chính.'))

            self.env['system.event'].safe_emit(
                'de_xuat.submitted',
                f'Đề xuất {record.ma_de_xuat} đã gửi',
                source_model='de_xuat_mua_tai_san',
                source_id=record.id,
                payload={
                    'ma_de_xuat': record.ma_de_xuat,
                    'ten_de_xuat': record.ten_de_xuat,
                    'phong_ban': record.phong_ban_id.ten_phong_ban if record.phong_ban_id else '—',
                    'tong_gia_tri': record.tong_gia_tri,
                    'phe_duyet_id': record.phe_duyet_id.id if record.phe_duyet_id else False,
                },
            )

    def _create_approval_request(self):
        """Tạo đơn phê duyệt tự động ở module tài chính"""
        self.ensure_one()

        if not self.env['ir.module.module'].search([
            ('name', '=', 'quan_ly_tai_chinh'), ('state', '=', 'installed')
        ]):
            raise UserError(_('Module Quản lý tài chính chưa được cài đặt.'))

        line_vals = []
        for line in self.line_ids:
            danh_muc_id = False
            if line.danh_muc_ts_id and line.danh_muc_ts_id.id:
                try:
                    if line.danh_muc_ts_id.exists():
                        danh_muc_id = line.danh_muc_ts_id.id
                except Exception:
                    pass
            if not danh_muc_id:
                raise UserError(_(
                    'Thiết bị "%s" chưa có danh mục tài sản hợp lệ.'
                ) % (line.ten_thiet_bi or ''))

            line_vals.append((0, 0, {
                'ten_thiet_bi': line.ten_thiet_bi or '',
                'danh_muc_ts_id': danh_muc_id,
                'mo_ta': line.mo_ta or '',
                'thong_so_ky_thuat': line.thong_so_ky_thuat or '',
                'so_luong': line.so_luong or 1,
                'don_vi_tinh': line.don_vi_tinh or '',
                'don_gia': line.don_gia or 0.0,
                'thanh_tien': line.thanh_tien or 0.0,
                'pp_khau_hao': line.pp_khau_hao or 'straight-line',
                'thoi_gian_su_dung': line.thoi_gian_su_dung or 0,
                'ty_le_khau_hao': line.ty_le_khau_hao or 0.0,
                'nha_cung_cap': line.nha_cung_cap or '',
            }))

        phe_duyet = self.env['phe_duyet_mua_tai_san'].create({
            'de_xuat_mua_id': self.id,
            'ten_de_xuat': self.ten_de_xuat or '',
            'ngay_de_xuat': self.ngay_de_xuat or fields.Date.today(),
            'nguoi_de_xuat_id': self.nguoi_de_xuat_id.id if self.nguoi_de_xuat_id else False,
            'nhan_vien_id': self.nhan_vien_id.id if self.nhan_vien_id else False,
            'phong_ban_id': self.phong_ban_id.id if self.phong_ban_id else False,
            'tong_gia_tri': self.tong_gia_tri or 0.0,
            'don_vi_tien_te': self.don_vi_tien_te or 'vnd',
            'ly_do': self.ly_do or '',
            'mo_ta': self.mo_ta or '',
            'ngay_du_kien_nhan': self.ngay_du_kien_nhan or False,
            'line_ids': line_vals,
        })
        self.phe_duyet_id = phe_duyet.id

        try:
            finance_users = self.env.ref('quan_ly_tai_chinh.group_finance_manager').users
            if finance_users:
                phe_duyet.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=finance_users[0].id,
                    summary=f'Phê duyệt đề xuất: {self.ma_de_xuat}',
                )
        except Exception:
            pass

        return phe_duyet

    def action_cancel(self):
        """Hủy đề xuất"""
        for record in self:
            if record.state == 'approved':
                raise UserError(_('Không thể hủy đề xuất đã phê duyệt.'))
            if record.phe_duyet_id and record.phe_duyet_id.state == 'draft':
                record.phe_duyet_id.action_cancel()
            record.state = 'cancelled'

    def action_reset_to_draft(self):
        """Reset về nháp từ rejected/cancelled/approved"""
        for record in self:
            record.with_context(force_reset=True, from_finance_approval=True).write({
                'state': 'draft',
                'phe_duyet_id': False,
            })
            record.message_post(body=_('Đề xuất đã được đặt lại về trạng thái Nháp.'))
        return True

    def action_view_approval(self):
        """Xem đơn phê duyệt"""
        self.ensure_one()
        if not self.phe_duyet_id:
            raise UserError(_('Chưa có đơn phê duyệt nào được tạo.'))
        return {
            'name': _('Đơn phê duyệt mua tài sản'),
            'type': 'ir.actions.act_window',
            'res_model': 'phe_duyet_mua_tai_san',
            'view_mode': 'form',
            'res_id': self.phe_duyet_id.id,
            'target': 'current',
        }

    def action_view_assets(self):
        """Xem tài sản đã tạo"""
        self.ensure_one()
        return {
            'name': _('Tài sản đã tạo'),
            'type': 'ir.actions.act_window',
            'res_model': 'tai_san',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.tai_san_ids.ids)],
            'context': {'create': False},
        }

    # ============ CALLBACKS TỪ MODULE TÀI CHÍNH ============
    def _on_approval_approved(self):
        self.ensure_one()
        self.with_context(from_finance_approval=True).write({'state': 'approved'})
        self.message_post(body=_('Đề xuất đã được phê duyệt bởi bộ phận tài chính.'))

    def _on_approval_rejected(self):
        self.ensure_one()
        self.with_context(from_finance_approval=True).write({'state': 'rejected'})
        self.message_post(body=_('Đề xuất đã bị từ chối bởi bộ phận tài chính.'))

    def _on_approval_deleted(self):
        self.ensure_one()
        try:
            self.with_context(from_finance_approval=True).write({
                'state': 'draft', 'phe_duyet_id': False,
            })
            self.message_post(body=_('Đơn phê duyệt đã bị xóa. Đề xuất trở về nháp.'))
        except Exception as e:
            _logger.warning("Could not reset de_xuat_mua_tai_san %s: %s", self.id, e)


class DeXuatMuaTaiSanLine(models.Model):
    """Chi tiết đề xuất mua tài sản"""
    _name = 'de_xuat_mua_tai_san.line'
    _description = 'Chi tiết đề xuất mua tài sản'
    _order = 'sequence, id'

    sequence = fields.Integer(string='STT', default=10)
    de_xuat_id = fields.Many2one(
        'de_xuat_mua_tai_san', string='Đề xuất',
        required=True, ondelete='cascade', index=True,
    )

    # ============ THÔNG TIN THIẾT BỊ ============
    ten_thiet_bi = fields.Char(string='Tên thiết bị', required=True)
    danh_muc_ts_id = fields.Many2one(
        'danh_muc_tai_san', string='Danh mục tài sản',
        required=False, ondelete='set null',
    )
    mo_ta = fields.Text(string='Mô tả')
    thong_so_ky_thuat = fields.Text(string='Thông số kỹ thuật')
    nha_cung_cap = fields.Char(string='Nhà cung cấp đề xuất')

    # ============ SỐ LƯỢNG VÀ GIÁ ============
    so_luong = fields.Integer(string='Số lượng', default=1, required=True)
    don_vi_tinh = fields.Char(string='Đơn vị tính', default='Chiếc', required=True)
    don_gia = fields.Float(string='Đơn giá', required=True)
    thanh_tien = fields.Float(string='Thành tiền', compute='_compute_thanh_tien', store=True)

    # ============ KHẤU HAO ============
    pp_khau_hao = fields.Selection([
        ('straight-line', 'Khấu hao tuyến tính'),
        ('degressive', 'Khấu hao giảm dần'),
        ('none', 'Không khấu hao'),
    ], string='Phương pháp khấu hao', default='straight-line', required=True)
    thoi_gian_su_dung = fields.Integer(string='Thời gian sử dụng (năm)', default=5)
    ty_le_khau_hao = fields.Float(
        string='Tỷ lệ khấu hao (%/năm)',
        compute='_compute_ty_le_khau_hao', store=True, readonly=False,
    )

    # ============ COMPUTE ============
    @api.depends('so_luong', 'don_gia')
    def _compute_thanh_tien(self):
        for r in self:
            r.thanh_tien = r.so_luong * r.don_gia

    @api.depends('thoi_gian_su_dung')
    def _compute_ty_le_khau_hao(self):
        for r in self:
            r.ty_le_khau_hao = (100.0 / r.thoi_gian_su_dung) if r.thoi_gian_su_dung > 0 else 0.0

    # ============ CONSTRAINTS ============
    @api.constrains('so_luong', 'don_gia')
    def _check_positive_values(self):
        for r in self:
            if r.so_luong <= 0:
                raise ValidationError(_('Số lượng phải lớn hơn 0.'))
            if r.don_gia < 0:
                raise ValidationError(_('Đơn giá không thể âm.'))

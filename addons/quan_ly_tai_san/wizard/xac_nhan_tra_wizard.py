# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class XacNhanTraWizardLine(models.TransientModel):
    """Chi tiết từng tài sản khi xác nhận trả"""
    _name = 'xac_nhan_tra_wizard_line'
    _description = 'Chi tiết xác nhận trả tài sản'

    wizard_id = fields.Many2one('xac_nhan_tra_wizard', string='Wizard', required=True, ondelete='cascade')
    don_muon_line_id = fields.Many2one('don_muon_tai_san_line', string='Dòng đơn mượn', ondelete='cascade')
    ten_tai_san = fields.Char('Tên tài sản', readonly=True)
    tinh_trang_khi_tra = fields.Selection([
        ('tot', 'Tốt'),
        ('binh_thuong', 'Bình thường'),
        ('hu_hong', 'Hư hỏng'),
        ('mat', 'Mất'),
    ], string='Tình trạng khi trả', default='tot', required=True)
    ghi_chu = fields.Text('Ghi chú')


class XacNhanTraWizard(models.TransientModel):
    """Wizard xác nhận trả tài sản — cho nhập tình trạng từng tài sản"""
    _name = 'xac_nhan_tra_wizard'
    _description = 'Xác nhận trả tài sản'

    don_muon_id = fields.Many2one('don_muon_tai_san', string='Đơn mượn', required=True)
    line_ids = fields.One2many('xac_nhan_tra_wizard_line', 'wizard_id', string='Danh sách tài sản')
    ghi_chu_chung = fields.Text('Ghi chú chung')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Tự động tạo lines từ đơn mượn
        don_muon_id = res.get('don_muon_id') or self.env.context.get('default_don_muon_id')
        if don_muon_id:
            don_muon = self.env['don_muon_tai_san'].browse(don_muon_id)
            lines = []
            for line in don_muon.don_muon_tai_san_ids:
                if line.phan_bo_tai_san_id:
                    ten = line.phan_bo_tai_san_id.tai_san_id.ten_tai_san if line.phan_bo_tai_san_id.tai_san_id else 'Tài sản'
                    lines.append((0, 0, {
                        'don_muon_line_id': line.id,
                        'ten_tai_san': ten,
                        'tinh_trang_khi_tra': 'tot',
                    }))
            res['line_ids'] = lines
        return res

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if not record.line_ids and record.don_muon_id:
            lines = []
            for line in record.don_muon_id.don_muon_tai_san_ids:
                if line.phan_bo_tai_san_id:
                    ten = line.phan_bo_tai_san_id.tai_san_id.ten_tai_san if line.phan_bo_tai_san_id.tai_san_id else 'Tài sản'
                    lines.append((0, 0, {
                        'don_muon_line_id': line.id,
                        'ten_tai_san': ten,
                        'tinh_trang_khi_tra': 'tot',
                    }))
            if lines:
                record.write({'line_ids': lines})
        return record

    def action_confirm(self):
        """Xác nhận trả — cập nhật tình trạng từng tài sản"""
        self.ensure_one()
        if not self.don_muon_id:
            raise UserError(_('Không tìm thấy đơn mượn!'))

        invalid = self.line_ids.filtered(lambda l: not l.don_muon_line_id)
        if invalid:
            invalid.unlink()
        if not self.line_ids:
            raise UserError(_(
                'Không có dòng tài sản để xác nhận trả. '
                'Đóng cửa sổ và mở lại thao tác trả.'
            ))

        don_muon = self.don_muon_id
        now = fields.Datetime.now()

        # Cập nhật tình trạng từng tài sản theo wizard lines
        for wiz_line in self.line_ids:
            if wiz_line.don_muon_line_id and wiz_line.don_muon_line_id.phan_bo_tai_san_id:
                phan_bo = wiz_line.don_muon_line_id.phan_bo_tai_san_id
                tinh_trang_moi = 'binh_thuong'
                if wiz_line.tinh_trang_khi_tra == 'hu_hong':
                    tinh_trang_moi = 'hu_hong'
                elif wiz_line.tinh_trang_khi_tra == 'mat':
                    tinh_trang_moi = 'mat'

                phan_bo.write({'tinh_trang': tinh_trang_moi})
                wiz_line.don_muon_line_id.write({
                    'tinh_trang_sau_tra': wiz_line.tinh_trang_khi_tra,
                    'thoi_gian_tra_thuc_te': now,
                    'nguoi_nhan_tra_id': self.env.user.id,
                    'trang_thai_line': 'da_tra' if wiz_line.tinh_trang_khi_tra in ['tot', 'binh_thuong'] else (
                        'mat' if wiz_line.tinh_trang_khi_tra == 'mat' else 'hong'
                    ),
                    'ghi_chu_tinh_trang': wiz_line.ghi_chu or '',
                })

        # Cập nhật đơn mượn
        don_muon.write({
            'trang_thai': 'da_tra',
            'ngay_tra_thuc_te': now,
            'nguoi_xac_nhan_tra_id': self.env.user.id,
        })

        don_muon.message_post(
            body=_('✅ Tài sản đã được trả lúc %s. Người nhận: %s.\n%s') % (
                now.strftime('%d/%m/%Y %H:%M'),
                self.env.user.name,
                self.ghi_chu_chung or '',
            )
        )

        return {'type': 'ir.actions.act_window_close'}

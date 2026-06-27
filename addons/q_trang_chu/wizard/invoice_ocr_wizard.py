# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import os

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')


class InvoiceOcrWizard(models.TransientModel):
    _name = 'invoice.ocr.wizard'
    _description = 'Wizard OCR hóa đơn'

    file_data = fields.Binary(string='Ảnh hóa đơn', required=True, attachment=True)
    file_name = fields.Char(string='Tên file')
    result_id = fields.Many2one('invoice.ocr.result', string='Kết quả', readonly=True)

    # Trạng thái để hiện thông báo trước khi gọi API
    ready_to_call = fields.Boolean(
        string='Xác nhận gọi AI',
        default=False,
        help='Tích vào để xác nhận muốn gọi Gemini AI phân tích hóa đơn (tiêu tốn quota API)')

    def _check_api_key(self):
        """Kiểm tra API key có sẵn không."""
        icp = self.env['ir.config_parameter'].sudo()
        key = icp.get_param('q_trang_chu.gemini_api_key') or GEMINI_API_KEY
        if not key:
            raise UserError(_(
                '⚠️ Chưa cấu hình Gemini API Key!\n\n'
                'Vào: Cài đặt → Tích hợp AI & Telegram → điền Gemini API Key.\n\n'
                'Hoặc đặt biến môi trường: GEMINI_API_KEY=your_key'
            ))
        return key

    def action_preview(self):
        """Bước 1: Xem trước file trước khi gọi API."""
        self.ensure_one()
        if not self.file_data:
            raise UserError(_('Vui lòng tải lên ảnh hóa đơn trước.'))
        # Kiểm tra API key sớm – báo lỗi ngay không chờ đến lúc gọi
        self._check_api_key()
        # Đánh dấu sẵn sàng
        self.ready_to_call = True
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_process_ocr(self):
        """Bước 2: Người dùng xác nhận → GỌI Gemini API phân tích."""
        self.ensure_one()
        if not self.file_data:
            raise UserError(_('Vui lòng tải lên ảnh hóa đơn.'))

        # Chỉ gọi API khi người dùng đã xác nhận (tích checkbox)
        if not self.ready_to_call:
            raise UserError(_(
                '⚠️ Vui lòng tích vào ô "Xác nhận gọi AI" để tiếp tục.\n\n'
                'Lưu ý: Mỗi lần phân tích sẽ tiêu tốn 1 lần gọi Gemini API quota.'
            ))

        # Kiểm tra API key lần cuối
        self._check_api_key()

        # Xác định mimetype
        fname = (self.file_name or '').lower()
        if fname.endswith('.png'):
            mime = 'image/png'
        elif fname.endswith('.pdf'):
            raise UserError(_(
                'OCR hiện chỉ hỗ trợ ảnh JPG/PNG.\n'
                'Vui lòng chụp ảnh hoặc chuyển đổi PDF sang ảnh trước.'
            ))
        else:
            mime = 'image/jpeg'

        # Tạo attachment
        attachment = self.env['ir.attachment'].create({
            'name': self.file_name or 'hoa_don.jpg',
            'datas': self.file_data,
            'mimetype': mime,
            'res_model': self._name,
            'res_id': self.id,
        })

        # ── GỌI GEMINI API – CHỈ XẢY RA TẠI ĐÂY ──────────────────
        result = self.env['invoice.ocr.service'].process_attachment(attachment)
        # ────────────────────────────────────────────────────────────

        self.result_id = result.id

        if result.state == 'error':
            raise UserError(_('❌ OCR thất bại: %s') % (result.error_message or 'Lỗi không xác định'))

        return {
            'type': 'ir.actions.act_window',
            'name': _('✅ Kết quả OCR hóa đơn'),
            'res_model': 'invoice.ocr.result',
            'view_mode': 'form',
            'res_id': result.id,
            'target': 'current',
        }

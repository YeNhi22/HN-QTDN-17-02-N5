# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InvoiceOcrWizard(models.TransientModel):
    _name = 'invoice.ocr.wizard'
    _description = 'Wizard OCR hóa đơn – Groq AI'

    file_data = fields.Binary(string='Ảnh hóa đơn (JPG/PNG)', required=True, attachment=True)
    file_name = fields.Char(string='Tên file')
    result_id = fields.Many2one('invoice.ocr.result', string='Kết quả', readonly=True)

    def _check_api_key(self):
        """Kiểm tra Groq API key đã được cấu hình chưa."""
        icp = self.env['ir.config_parameter'].sudo()
        key = (icp.get_param('q_trang_chu.gemini_api_key') or '').strip()
        if not key:
            import os
            key = (os.environ.get('GROQ_API_KEY') or '').strip()
        if not key:
            raise UserError(_(
                '⚠️ Chưa cấu hình Groq API Key!\n\n'
                'Vào: Thiết lập → Tích hợp AI & Telegram → điền Groq API Key.\n\n'
                'Lấy key miễn phí tại: https://console.groq.com/keys'
            ))
        return key

    def action_process_ocr(self):
        """Upload ảnh → kiểm tra key → phân tích OCR bằng Groq AI."""
        self.ensure_one()
        if not self.file_data:
            raise UserError(_('Vui lòng tải lên ảnh hóa đơn (JPG/PNG).'))

        # Kiểm tra key trước khi gọi API
        self._check_api_key()

        fname = (self.file_name or '').lower()
        if fname.endswith('.png'):
            mime = 'image/png'
        elif fname.endswith('.pdf'):
            raise UserError(_('OCR hỗ trợ ảnh JPG/PNG. Vui lòng chụp ảnh hóa đơn.'))
        else:
            mime = 'image/jpeg'

        attachment = self.env['ir.attachment'].create({
            'name': self.file_name or 'hoa_don.jpg',
            'datas': self.file_data,
            'mimetype': mime,
            'res_model': self._name,
            'res_id': self.id,
        })

        result = self.env['invoice.ocr.service'].process_attachment(attachment)
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

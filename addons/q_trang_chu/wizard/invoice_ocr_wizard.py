# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import os

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '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')


class InvoiceOcrWizard(models.TransientModel):
    _name = 'invoice.ocr.wizard'
    _description = 'Wizard OCR hóa đơn'

    file_data = fields.Binary(string='Ảnh hóa đơn', required=True, attachment=True)
    file_name = fields.Char(string='Tên file')
    result_id = fields.Many2one('invoice.ocr.result', string='Kết quả', readonly=True)

    def action_process_ocr(self):
        """Upload ảnh → phân tích OCR bằng Groq AI ngay lập tức."""
        self.ensure_one()
        if not self.file_data:
            raise UserError(_('Vui lòng tải lên ảnh hóa đơn (JPG/PNG).'))

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
            'name': _('Kết quả OCR hóa đơn'),
            'res_model': 'invoice.ocr.result',
            'view_mode': 'form',
            'res_id': result.id,
            'target': 'current',
        }

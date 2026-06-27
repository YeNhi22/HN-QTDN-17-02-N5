# -*- coding: utf-8 -*-
import base64
import json
import logging
import os
import re

import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_VISION_URL = (
    'https://generativelanguage.googleapis.com/v1beta/models/'
    'gemini-2.0-flash:generateContent'
)

OCR_PROMPT = """Bạn là chuyên gia OCR hóa đơn Việt Nam.
Phân tích hình ảnh hóa đơn và trả về JSON thuần (không markdown) với các trường:
{
  "nha_cung_cap": "tên nhà cung cấp",
  "so_hoa_don": "số hóa đơn",
  "ngay_hoa_don": "YYYY-MM-DD",
  "tong_tien": số (VNĐ, không có dấu phẩy),
  "thue_vat": số hoặc 0,
  "chi_tiet": [{"ten": "tên hàng", "so_luong": 1, "don_gia": 0, "thanh_tien": 0}]
}
Nếu không đọc được, trả về {"error": "lý do"}."""


class InvoiceOcrResult(models.Model):
    """Kết quả OCR hóa đơn (Mức 3 — AI)."""
    _name = 'invoice.ocr.result'
    _description = 'Kết quả OCR hóa đơn'
    _order = 'create_date desc'

    name = fields.Char(string='Tên file', required=True)
    attachment_id = fields.Many2one('ir.attachment', string='File đính kèm', ondelete='set null')
    raw_json = fields.Text(string='JSON thô')
    nha_cung_cap = fields.Char(string='Nhà cung cấp')
    so_hoa_don = fields.Char(string='Số hóa đơn')
    ngay_hoa_don = fields.Date(string='Ngày hóa đơn')
    tong_tien = fields.Float(string='Tổng tiền')
    thue_vat = fields.Float(string='Thuế VAT')
    chi_tiet = fields.Text(string='Chi tiết (JSON)')
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('done', 'Hoàn thành'),
        ('error', 'Lỗi'),
    ], default='draft', required=True)
    error_message = fields.Text(string='Lỗi')
    de_xuat_id = fields.Many2one('de_xuat_mua_tai_san', string='Đề xuất đã tạo', readonly=True)

    def action_create_de_xuat(self):
        """Tạo đề xuất mua tài sản từ kết quả OCR."""
        self.ensure_one()
        if self.state != 'done':
            raise UserError(_('Chỉ có thể tạo đề xuất từ OCR đã hoàn thành.'))
        if 'de_xuat_mua_tai_san' not in self.env:
            raise UserError(_('Module Quản lý tài sản chưa được cài đặt.'))

        line_vals = []
        try:
            items = json.loads(self.chi_tiet or '[]')
        except json.JSONDecodeError:
            items = []

        if items:
            for item in items:
                line_vals.append((0, 0, {
                    'ten_thiet_bi': item.get('ten', 'Thiết bị từ hóa đơn'),
                    'so_luong': int(item.get('so_luong', 1) or 1),
                    'don_gia': float(item.get('don_gia', 0) or 0),
                    'don_vi_tinh': 'Chiếc',
                    'nha_cung_cap': self.nha_cung_cap or '',
                }))
        else:
            line_vals.append((0, 0, {
                'ten_thiet_bi': f'Hàng hóa từ HĐ {self.so_hoa_don or ""}',
                'so_luong': 1,
                'don_gia': self.tong_tien or 0,
                'don_vi_tinh': 'Bộ',
                'nha_cung_cap': self.nha_cung_cap or '',
            }))

        de_xuat = self.env['de_xuat_mua_tai_san'].create({
            'ten_de_xuat': f'Đề xuất từ OCR — {self.so_hoa_don or self.name}',
            'ly_do': f'Tự động tạo từ OCR hóa đơn {self.so_hoa_don or ""} — NCC: {self.nha_cung_cap or ""}',
            'line_ids': line_vals,
        })
        self.de_xuat_id = de_xuat.id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Đề xuất mua tài sản'),
            'res_model': 'de_xuat_mua_tai_san',
            'view_mode': 'form',
            'res_id': de_xuat.id,
            'target': 'current',
        }


class InvoiceOcrService(models.AbstractModel):
    """Dịch vụ OCR hóa đơn qua Gemini Vision API."""
    _name = 'invoice.ocr.service'
    _description = 'Invoice OCR Service'

    @api.model
    def _get_api_key(self):
        icp = self.env['ir.config_parameter'].sudo()
        return icp.get_param('q_trang_chu.gemini_api_key') or GEMINI_API_KEY

    @api.model
    def extract_from_attachment(self, attachment):
        """Gọi Gemini Vision để bóc tách dữ liệu hóa đơn."""
        if not attachment:
            raise UserError(_('Không có file đính kèm.'))

        api_key = self._get_api_key()
        if not api_key:
            raise UserError(_(
                'Chưa cấu hình GEMINI_API_KEY.\n'
                'Vào Cài đặt → Tích hợp AI & Telegram hoặc đặt biến môi trường.'
            ))

        data = attachment.datas
        if not data:
            raise UserError(_('File rỗng hoặc không đọc được.'))

        mime = attachment.mimetype or 'image/jpeg'
        if mime == 'application/pdf':
            raise UserError(_('Hiện tại OCR hỗ trợ ảnh (JPG/PNG). Vui lòng chụp ảnh hóa đơn.'))

        b64_data = attachment.datas
        if isinstance(b64_data, bytes):
            b64_data = b64_data.decode('utf-8')

        url = f'{GEMINI_VISION_URL}?key={api_key}'
        payload = {
            'contents': [{
                'parts': [
                    {'text': OCR_PROMPT},
                    {'inline_data': {'mime_type': mime, 'data': b64_data}},
                ],
            }],
            'generationConfig': {'temperature': 0.1, 'maxOutputTokens': 2048},
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code != 200:
                raise UserError(_('Gemini API lỗi %s: %s') % (response.status_code, response.text[:200]))
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
        except UserError:
            raise
        except Exception as exc:
            _logger.exception('OCR failed')
            raise UserError(_('Lỗi OCR: %s') % str(exc)) from exc

        return self._parse_ocr_response(text)

    @api.model
    def _parse_ocr_response(self, text):
        """Parse JSON từ phản hồi Gemini."""
        cleaned = text.strip()
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {'error': 'Không parse được JSON từ AI', 'raw': text}

    @api.model
    def process_attachment(self, attachment):
        """Xử lý OCR và lưu kết quả."""
        parsed = self.extract_from_attachment(attachment)
        if parsed.get('error'):
            return self.env['invoice.ocr.result'].create({
                'name': attachment.name or 'OCR Error',
                'attachment_id': attachment.id,
                'raw_json': json.dumps(parsed, ensure_ascii=False),
                'state': 'error',
                'error_message': parsed.get('error'),
            })

        ngay = parsed.get('ngay_hoa_don')
        ngay_val = False
        if ngay and re.match(r'\d{4}-\d{2}-\d{2}', str(ngay)):
            ngay_val = ngay

        return self.env['invoice.ocr.result'].create({
            'name': attachment.name or 'Hóa đơn OCR',
            'attachment_id': attachment.id,
            'raw_json': json.dumps(parsed, ensure_ascii=False),
            'nha_cung_cap': parsed.get('nha_cung_cap', ''),
            'so_hoa_don': parsed.get('so_hoa_don', ''),
            'ngay_hoa_don': ngay_val,
            'tong_tien': float(parsed.get('tong_tien', 0) or 0),
            'thue_vat': float(parsed.get('thue_vat', 0) or 0),
            'chi_tiet': json.dumps(parsed.get('chi_tiet', []), ensure_ascii=False),
            'state': 'done',
        })

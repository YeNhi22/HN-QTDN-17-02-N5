# -*- coding: utf-8 -*-
import json
import logging
import os
import re

import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Key lấy từ biến môi trường hoặc Odoo Settings – KHÔNG hardcode
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_VISION_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_VISION_MODEL = 'meta-llama/llama-4-scout-17b-16e-instruct'

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
    """Kết quả OCR hóa đơn."""
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

    # Field HTML trực quan cho chi tiết hàng hóa
    chi_tiet_html = fields.Html(
        string='Chi tiết hàng hóa',
        compute='_compute_chi_tiet_html',
        sanitize=False,
    )

    @api.depends('chi_tiet', 'tong_tien', 'thue_vat')
    def _compute_chi_tiet_html(self):
        """Render chi tiết hàng hóa dạng bảng HTML đẹp."""
        for rec in self:
            try:
                items = json.loads(rec.chi_tiet or '[]')
            except Exception:
                rec.chi_tiet_html = '<p class="text-muted">Không có dữ liệu chi tiết.</p>'
                continue

            if not items:
                rec.chi_tiet_html = '<p class="text-muted">Không có hàng hóa nào.</p>'
                continue

            rows = ''
            for i, item in enumerate(items, 1):
                ten = item.get('ten', '')
                sl = item.get('so_luong', 1)
                don_gia = item.get('don_gia', 0)
                thanh_tien = item.get('thanh_tien', 0)
                rows += f'''
                <tr style="border-bottom:1px solid #e5e7eb;">
                    <td style="padding:10px 8px;text-align:center;color:#6b7280;">{i}</td>
                    <td style="padding:10px 8px;font-weight:500;">{ten}</td>
                    <td style="padding:10px 8px;text-align:center;">{sl}</td>
                    <td style="padding:10px 8px;text-align:right;color:#374151;">{don_gia:,.0f}</td>
                    <td style="padding:10px 8px;text-align:right;font-weight:600;color:#1d4ed8;">{thanh_tien:,.0f}</td>
                </tr>'''

            tong = rec.tong_tien or sum(i.get('thanh_tien', 0) for i in items)
            vat = rec.thue_vat or 0
            tong_cong = tong + vat

            html = f'''
<div style="font-family:'Segoe UI',sans-serif;border-radius:10px;overflow:hidden;
            border:1px solid #e5e7eb;margin-top:4px;">
  <table style="width:100%;border-collapse:collapse;">
    <thead>
      <tr style="background:linear-gradient(90deg,#1e3a5f,#2d6a9f);color:white;">
        <th style="padding:12px 8px;text-align:center;width:40px;">#</th>
        <th style="padding:12px 8px;text-align:left;">Tên hàng hóa</th>
        <th style="padding:12px 8px;text-align:center;width:70px;">SL</th>
        <th style="padding:12px 8px;text-align:right;width:130px;">Đơn giá (VNĐ)</th>
        <th style="padding:12px 8px;text-align:right;width:140px;">Thành tiền (VNĐ)</th>
      </tr>
    </thead>
    <tbody style="background:#fff;">
      {rows}
    </tbody>
    <tfoot>
      <tr style="background:#f8fafc;">
        <td colspan="4" style="padding:10px 8px;text-align:right;font-weight:600;color:#374151;">
          Thuế VAT:
        </td>
        <td style="padding:10px 8px;text-align:right;color:#dc2626;">{vat:,.0f}</td>
      </tr>
      <tr style="background:#eff6ff;">
        <td colspan="4" style="padding:12px 8px;text-align:right;font-weight:700;
                                color:#1e40af;font-size:14px;">
          TỔNG CỘNG:
        </td>
        <td style="padding:12px 8px;text-align:right;font-weight:800;
                   color:#1e40af;font-size:15px;">{tong_cong:,.0f}</td>
      </tr>
    </tfoot>
  </table>
</div>'''
            rec.chi_tiet_html = html

    def action_create_de_xuat(self):
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
    """Dịch vụ OCR hóa đơn qua Groq Vision API."""
    _name = 'invoice.ocr.service'
    _description = 'Invoice OCR Service'

    @api.model
    def _get_api_key(self):
        """Lấy Groq API key từ Odoo Settings (Thiết lập → Tích hợp AI)."""
        icp = self.env['ir.config_parameter'].sudo()
        key = (icp.get_param('q_trang_chu.gemini_api_key') or '').strip()
        if not key:
            # Fallback về biến môi trường nếu chưa set trong Settings
            key = os.environ.get('GROQ_API_KEY', '').strip()
        return key

    @api.model
    def extract_from_attachment(self, attachment):
        if not attachment:
            raise UserError(_('Không có file đính kèm.'))
        api_key = self._get_api_key()
        if not api_key:
            raise UserError(_('Chưa cấu hình API Key.'))
        data = attachment.datas
        if not data:
            raise UserError(_('File rỗng hoặc không đọc được.'))
        mime = attachment.mimetype or 'image/jpeg'
        if mime == 'application/pdf':
            raise UserError(_('OCR hỗ trợ ảnh JPG/PNG. Vui lòng chụp ảnh hóa đơn.'))
        b64_data = attachment.datas
        if isinstance(b64_data, bytes):
            b64_data = b64_data.decode('utf-8')
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        payload = {
            'model': GROQ_VISION_MODEL,
            'messages': [{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': OCR_PROMPT},
                    {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{b64_data}'}},
                ],
            }],
            'temperature': 0.1,
            'max_tokens': 2048,
        }
        try:
            response = requests.post(GROQ_VISION_URL, headers=headers, json=payload, timeout=60)
            if response.status_code != 200:
                raise UserError(_('API lỗi %s: %s') % (response.status_code, response.text[:300]))
            text = response.json()['choices'][0]['message']['content']
        except UserError:
            raise
        except Exception as exc:
            _logger.exception('OCR failed')
            raise UserError(_('Lỗi OCR: %s') % str(exc)) from exc
        return self._parse_ocr_response(text)

    @api.model
    def _parse_ocr_response(self, text):
        cleaned = text.strip()
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return {'error': 'Không parse được JSON từ AI', 'raw': text}

    @api.model
    def process_attachment(self, attachment):
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

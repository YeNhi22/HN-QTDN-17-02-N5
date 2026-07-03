# -*- coding: utf-8 -*-
import json
import logging
import urllib.request
import urllib.error

from odoo import models, _

_logger = logging.getLogger(__name__)

# Số lượng tin nhắn lịch sử giữ lại để gửi cho Gemini (context)
HISTORY_LIMIT = 10


class MailBotGemini(models.AbstractModel):
    _inherit = 'mail.bot'

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _gemini_get_api_key(self):
        """Lấy Gemini API key từ System Parameters."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'mail_bot_gemini.api_key', default=''
        )

    def _gemini_get_model(self):
        """Lấy tên model Gemini, mặc định gemini-1.5-flash."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'mail_bot_gemini.model', default='gemini-1.5-flash'
        )

    def _gemini_get_system_prompt(self):
        """Lấy system prompt tùy chỉnh từ System Parameters."""
        default_prompt = (
            "Bạn là OdooBot, trợ lý AI thân thiện và chuyên nghiệp của hệ thống "
            "quản lý doanh nghiệp Odoo. Hãy trả lời ngắn gọn, hữu ích và thân thiện. "
            "Nếu được hỏi về các tính năng Odoo, hãy hướng dẫn người dùng một cách rõ ràng. "
            "Trả lời bằng ngôn ngữ mà người dùng đang dùng."
        )
        return self.env['ir.config_parameter'].sudo().get_param(
            'mail_bot_gemini.system_prompt', default=default_prompt
        )

    def _gemini_build_history(self, record):
        """
        Lấy lịch sử hội thoại gần nhất trong channel để gửi kèm cho Gemini.
        Trả về list các dict theo định dạng Gemini contents.
        """
        if record._name != 'mail.channel':
            return []

        odoobot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")

        # Lấy các tin nhắn gần nhất (trừ tin đang xử lý — chưa được lưu)
        messages = self.env['mail.message'].search([
            ('res_id', '=', record.id),
            ('model', '=', 'mail.channel'),
            ('message_type', 'in', ['comment', 'email']),
            ('subtype_id', '=', self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')),
        ], order='id desc', limit=HISTORY_LIMIT)

        history = []
        for msg in reversed(messages):
            # Loại bỏ HTML tags đơn giản
            import re
            body = re.sub(r'<[^>]+>', ' ', msg.body or '').strip()
            body = re.sub(r'\s+', ' ', body).strip()
            if not body:
                continue

            role = 'model' if msg.author_id.id == odoobot_id else 'user'
            history.append({
                'role': role,
                'parts': [{'text': body}]
            })

        return history

    def _gemini_call_api(self, user_message, history=None):
        """
        Gọi Gemini API và trả về chuỗi câu trả lời.
        Trả về None nếu có lỗi.
        """
        api_key = self._gemini_get_api_key()
        if not api_key:
            _logger.warning(
                "Gemini API key chưa được cấu hình. "
                "Vào Settings > Technical > System Parameters, "
                "thêm key: mail_bot_gemini.api_key"
            )
            return None

        model_name = self._gemini_get_model()
        system_prompt = self._gemini_get_system_prompt()

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={api_key}"
        )

        # Xây dựng contents: lịch sử + tin nhắn hiện tại
        contents = list(history or [])
        contents.append({
            'role': 'user',
            'parts': [{'text': user_message}]
        })

        payload = {
            'system_instruction': {
                'parts': [{'text': system_prompt}]
            },
            'contents': contents,
            'generationConfig': {
                'temperature': 0.7,
                'maxOutputTokens': 1024,
            },
            'safetySettings': [
                {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
                {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
            ]
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))

            candidates = result.get('candidates', [])
            if not candidates:
                _logger.warning("Gemini API trả về không có candidates: %s", result)
                return None

            parts = candidates[0].get('content', {}).get('parts', [])
            if not parts:
                return None

            return parts[0].get('text', '').strip()

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='replace')
            _logger.error("Gemini API HTTP error %s: %s", e.code, error_body)
            return None
        except urllib.error.URLError as e:
            _logger.error("Gemini API không thể kết nối: %s", e.reason)
            return None
        except Exception as e:
            _logger.exception("Lỗi không xác định khi gọi Gemini API: %s", e)
            return None

    # ------------------------------------------------------------------
    # Override _get_answer
    # ------------------------------------------------------------------

    def _get_answer(self, record, body, values, command=False):
        """
        Override _get_answer để tích hợp Gemini AI.

        Luồng xử lý:
        1. Gọi super() để chạy logic onboarding gốc trước.
        2. Nếu super() đã trả lời → dùng câu trả lời đó (giữ onboarding nguyên vẹn).
        3. Nếu super() trả về False (bot không hiểu) VÀ bot đang ở trạng thái idle
           trong private channel → gọi Gemini API.
        4. Nếu Gemini thất bại → fallback về câu trả lời mặc định.
        """
        # Bước 1: Thử logic gốc trước (onboarding, easter eggs, help, v.v.)
        original_answer = super()._get_answer(record, body, values, command)

        # Bước 2: Nếu có câu trả lời từ logic gốc → giữ nguyên
        if original_answer:
            return original_answer

        # Bước 3: Bot không hiểu, bot đang idle trong private channel → gọi Gemini
        if not self._is_bot_in_private_channel(record):
            return False

        odoobot_state = self.env.user.odoobot_state
        # Chỉ gọi Gemini khi ở trạng thái idle (đã qua onboarding)
        if odoobot_state not in ('idle', False, 'not_initialized'):
            return False

        # Lấy lịch sử chat để cung cấp context cho Gemini
        history = self._gemini_build_history(record)

        # Lấy lại body gốc (chưa lowercase) từ values để Gemini nhận đúng văn bản
        raw_body = values.get('body', body)
        import re
        clean_body = re.sub(r'<[^>]+>', ' ', raw_body or '').strip()
        clean_body = re.sub(r'\s+', ' ', clean_body).strip()

        if not clean_body:
            return False

        gemini_answer = self._gemini_call_api(clean_body, history=history)

        if gemini_answer:
            # Chuyển newlines thành <br/> cho HTML display trong chat
            html_answer = gemini_answer.replace('\n', '<br/>')
            return html_answer

        # Bước 4: Fallback nếu Gemini thất bại
        _logger.info(
            "Gemini không trả lời được, dùng fallback cho message: %s", clean_body
        )
        return _(
            "Xin lỗi, tôi đang gặp sự cố kết nối 😅 "
            "Vui lòng thử lại sau hoặc liên hệ bộ phận hỗ trợ."
        )

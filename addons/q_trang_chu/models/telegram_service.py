# -*- coding: utf-8 -*-
import logging
import os

import requests

from odoo import models, api

_logger = logging.getLogger(__name__)


class TelegramNotificationService(models.AbstractModel):
    """Dịch vụ gửi thông báo qua Telegram Bot API (Mức 3 — External API)."""
    _name = 'telegram.notification.service'
    _description = 'Telegram Notification Service'

    @api.model
    def _get_config(self):
        icp = self.env['ir.config_parameter'].sudo()
        token = icp.get_param('q_trang_chu.telegram_bot_token') or os.environ.get('TELEGRAM_BOT_TOKEN', '')
        chat_id = icp.get_param('q_trang_chu.telegram_chat_id') or os.environ.get('TELEGRAM_CHAT_ID', '')
        enabled = icp.get_param('q_trang_chu.telegram_enabled', 'False') == 'True'
        if not enabled and os.environ.get('TELEGRAM_BOT_TOKEN'):
            enabled = True
        return token, chat_id, enabled

    @api.model
    def send_message(self, text, parse_mode='HTML'):
        token, chat_id, enabled = self._get_config()
        if not enabled or not token or not chat_id:
            _logger.debug('Telegram disabled or not configured')
            return False

        url = f'https://api.telegram.org/bot{token}/sendMessage'
        try:
            response = requests.post(
                url,
                json={
                    'chat_id': chat_id,
                    'text': text[:4096],
                    'parse_mode': parse_mode,
                    'disable_web_page_preview': True,
                },
                timeout=15,
            )
            if response.status_code != 200:
                _logger.warning('Telegram API error %s: %s', response.status_code, response.text)
                return False
            return True
        except Exception as exc:
            _logger.error('Telegram send failed: %s', exc)
            return False

    @api.model
    def test_connection(self):
        """Kiểm tra kết nối Telegram."""
        ok = self.send_message('🔔 <b>Test kết nối Telegram</b>\nHệ thống Quản lý Tài sản & Tài chính hoạt động bình thường.')
        return ok

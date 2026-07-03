# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    telegram_enabled = fields.Boolean(
        string='Bật Telegram',
        config_parameter='q_trang_chu.telegram_enabled',
    )
    telegram_bot_token = fields.Char(
        string='Telegram Bot Token',
        config_parameter='q_trang_chu.telegram_bot_token',
    )
    telegram_chat_id = fields.Char(
        string='Telegram Chat ID',
        config_parameter='q_trang_chu.telegram_chat_id',
    )
    gemini_api_key = fields.Char(
        string='API Key (Groq/AI)',
        config_parameter='q_trang_chu.gemini_api_key',
    )
    auto_post_depreciation = fields.Boolean(
        string='Tự động ghi sổ khấu hao (Cron)',
        config_parameter='q_trang_chu.auto_post_depreciation',
        default=True,
    )

    def action_test_telegram(self):
        self.ensure_one()
        self.env['telegram.notification.service'].test_connection()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Telegram',
                'message': 'Đã gửi tin nhắn test (nếu cấu hình đúng).',
                'type': 'info',
                'sticky': False,
            },
        }

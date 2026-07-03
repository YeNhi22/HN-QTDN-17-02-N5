# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gemini_api_key = fields.Char(
        string='Gemini API Key',
        config_parameter='mail_bot_gemini.api_key',
        help='Google Gemini API Key. Lấy tại https://aistudio.google.com/app/apikey'
    )
    gemini_model = fields.Char(
        string='Gemini Model',
        config_parameter='mail_bot_gemini.model',
        default='gemini-1.5-flash',
        help='Tên model Gemini (vd: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash)'
    )
    gemini_system_prompt = fields.Char(
        string='System Prompt',
        config_parameter='mail_bot_gemini.system_prompt',
        help='Prompt hệ thống để định hướng hành vi của bot. Để trống để dùng mặc định.'
    )

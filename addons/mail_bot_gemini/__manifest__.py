# -*- coding: utf-8 -*-
{
    'name': 'OdooBot with Gemini AI',
    'version': '1.0.0',
    'category': 'Productivity/Discuss',
    'summary': 'Tích hợp Google Gemini AI vào OdooBot để trả lời thông minh hơn',
    'description': """
OdooBot với Gemini AI
=====================
Module này mở rộng OdooBot bằng cách tích hợp Google Gemini API.
Khi bot không hiểu câu hỏi (trạng thái idle), thay vì trả lời ngẫu nhiên,
bot sẽ gọi Gemini API để tạo câu trả lời thông minh.

Cách cài đặt:
- Vào Settings > Technical > System Parameters
- Thêm key: mail_bot_gemini.api_key với value là Gemini API key của bạn
- Tuỳ chọn: mail_bot_gemini.model (mặc định: gemini-1.5-flash)
- Tuỳ chọn: mail_bot_gemini.system_prompt (prompt hệ thống tùy chỉnh)
    """,
    'depends': ['mail_bot'],
    'data': [
        'data/gemini_config_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}

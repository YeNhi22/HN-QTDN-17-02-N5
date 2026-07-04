# -*- coding: utf-8 -*-
{
    'name': "Trang chủ ",

    'summary': """
        Dashboard tổng quan và AI Chatbot hỗ trợ quản lý tài sản & tài chính""",

    'description': """
        Module Trang chủ tích hợp:
        - Dashboard tổng quan từ Quản lý Tài sản và Quản lý Tài chính
        - AI Chatbot Assistant 24/7
        - Thống kê, biểu đồ trực quan
        - Hướng dẫn quy trình tự động
        - OCR hóa đơn qua Gemini AI
        - Tích hợp Telegram thông báo
    """,

    'author': "Hoàng Phương Huế",
    'website': "http://www.yourcompany.com",
    'category': 'Productivity',
    'version': '1.0',
    'license': 'LGPL-3',

    # Dependencies
    'depends': [
        'base',
        'web',
        'mail',
        'base_setup',
        'nhan_su',
        'quan_ly_tai_san',
        'quan_ly_tai_chinh',
    ],

    'external_dependencies': {
        'python': ['requests'],
    },

    # Data files — thứ tự quan trọng:
    # 1. Security models cũ trước
    # 2. Views (định nghĩa models mới qua ORM)
    # 3. Security models mới sau khi models đã tồn tại
    # 4. Menu cuối cùng
    'data': [
        'security/ir.model.access.csv',
        'security/chatbot_security.xml',
        'data/chatbot_knowledge_data.xml',
        'views/dashboard_views.xml',
        'views/chatbot_views.xml',
        'views/integration_views.xml',
        'security/ocr_security.xml',
        'views/menu.xml',
        'views/hide_menus.xml',
    ],

    # Assets
    'assets': {
        'web.assets_backend': [
            # CSS
            'q_trang_chu/static/src/css/dashboard.css',
            'q_trang_chu/static/src/css/chatbot.css',
            'q_trang_chu/static/src/css/chatbot_page.css',
            # JS
            'q_trang_chu/static/src/js/chatbot_bubble.js',
            'q_trang_chu/static/src/js/dashboard.js',
            'q_trang_chu/static/src/js/chatbot_widget.js',
            'q_trang_chu/static/src/js/chatbot_page.js',
            # OWL XML Templates
            'q_trang_chu/static/src/xml/dashboard_templates.xml',
            'q_trang_chu/static/src/xml/chatbot_templates.xml',
            'q_trang_chu/static/src/xml/chatbot_page.xml',
        ],
    },

    'application': True,
    'installable': True,
    'auto_install': False,
}

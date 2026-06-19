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
        'quan_ly_tai_san',
        'quan_ly_tai_chinh',
    ],

    # Data files
    # Cải tiến từ phiên bản cũ: Sắp xếp lại thứ tự load - views trước, menu sau
    'data': [
        'security/ir.model.access.csv',
        'data/chatbot_knowledge_data.xml',
        'views/dashboard_views.xml',  # Load views và actions trước
        'views/chatbot_views.xml',     # Load tất cả views và actions
        'views/menu.xml',               # Load menu cuối cùng (menu tham chiếu actions)
    ],

    # Assets
    'assets': {
        'web.assets_backend': [
            # CSS
            'q_trang_chu/static/src/css/dashboard.css',
            'q_trang_chu/static/src/css/chatbot.css',
            'q_trang_chu/static/src/css/messenger_chat.css',
            'q_trang_chu/static/src/css/chatbot_page.css',
            # JS
            'q_trang_chu/static/src/js/dashboard.js',
            'q_trang_chu/static/src/js/messenger_chat.js',
            'q_trang_chu/static/src/js/chatbot_widget.js',
        ],
        'web.assets_qweb': [
            'q_trang_chu/static/src/xml/dashboard_templates.xml',
            'q_trang_chu/static/src/xml/messenger_chat.xml',
            'q_trang_chu/static/src/xml/chatbot_page.xml',
        ],
    },

    'application': True,
    'installable': True,
    'auto_install': False,
}


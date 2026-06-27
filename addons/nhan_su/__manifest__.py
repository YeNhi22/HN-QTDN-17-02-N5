# -*- coding: utf-8 -*-
{
    'name': "nhan_su",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/nhan_vien.xml',
         'views/phong_ban.xml',
         'views/chuc_vu.xml',
         'views/lich_su_cong_tac.xml',
        'views/menu.xml',
        'views/integration_views.xml',
    ],
    
    # Assets - Modern UI CSS
    'assets': {
        'web.assets_backend': [
            'nhan_su/static/src/css/hrm_modern.css',
        ],
    },
    
    # Dữ liệu mẫu — chỉ load khi tạo DB có tick "Demo data"
    'demo': [
        'data/qlns_demo.xml',
    ],
    'installable': True,
    'application': True,

}

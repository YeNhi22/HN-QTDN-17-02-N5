# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json


class NhanSuPortal(http.Controller):
    """
    Controller phục vụ Employee Portal và xử lý CORS
    cho web app nhân viên.
    """

    # ── Serve trang Employee Portal ──────────────────────────
    @http.route('/portal', auth='public', type='http', website=False, csrf=False)
    def employee_portal(self, **kw):
        """Trả về trang Employee Portal – truy cập tại http://localhost:8069/portal"""
        import os
        portal_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'portal', 'index.html'
        )
        if os.path.exists(portal_path):
            with open(portal_path, 'r', encoding='utf-8') as f:
                html = f.read()
            return Response(html, content_type='text/html; charset=utf-8')
        return Response('<h2>Portal chưa được cài đặt</h2>', content_type='text/html')

    # ── CORS preflight cho JSON-RPC ──────────────────────────
    @http.route([
        '/web/dataset/call_kw',
        '/web/session/authenticate',
        '/web/session/get_session_info',
    ], type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def cors_preflight(self, **kw):
        """Xử lý CORS preflight request từ web app."""
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, X-Requested-With',
            'Access-Control-Max-Age': '86400',
        }
        return Response(status=200, headers=headers)

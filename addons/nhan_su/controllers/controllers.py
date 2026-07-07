# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


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

    # ── API: Đăng nhập không ảnh hưởng session Odoo backend ────────────────
    @http.route('/api/nhan_su/login', auth='public', type='json', csrf=False, cors='*')
    def api_login(self, username, password, **kw):
        try:
            # Gọi trực tiếp method web_login của nhan_vien (chạy bằng sudo)
            res = request.env['nhan_vien'].sudo().web_login(username, password)
            if res.get('success'):
                # Sinh portal token để xác thực các request sau
                employee_id = res['employee']['id']
                employee = request.env['nhan_vien'].sudo().browse(employee_id)
                token = request.env['hrm.portal.token'].sudo().create_token(employee)
                res['token'] = token
            return res
        except Exception as e:
            return {'success': False, 'message': str(e)}

    # ── API: Thực hiện RPC cuộc gọi an toàn (chỉ cho phép một số model & method) ──
    @http.route('/api/nhan_su/rpc', auth='public', type='json', csrf=False, cors='*')
    def api_rpc(self, token, model, method, args=None, kwargs=None, **kw):
        args = args or []
        kwargs = kwargs or {}

        # Xác thực token
        employee = request.env['hrm.portal.token'].sudo().resolve(token)
        if not employee:
            raise ValidationError('Phiên làm việc hết hạn hoặc token không hợp lệ. Vui lòng đăng nhập lại.')

        # Ràng buộc bảo mật: Chỉ cho phép gọi các model và method cụ thể từ portal
        allowed_models_methods = {
            'nhan_vien': {'search_read', 'web_change_password', 'read'},
            'phan_bo_tai_san': {'search_read', 'read'},
            'don_muon_tai_san': {'search_read', 'read', 'create', 'action_gui_duyet'},
            'phong_ban': {'search_read', 'read'},
            'chuc_vu': {'search_read', 'read'}
        }

        if model not in allowed_models_methods:
            raise UserError(f'Truy cập mô hình "{model}" bị từ chối.')
        if method not in allowed_models_methods[model]:
            raise UserError(f'Thao tác phương thức "{method}" trên mô hình "{model}" bị từ chối.')

        try:
            # Chạy sudo để thực thi cuộc gọi hệ thống được ủy quyền
            model_sudo = request.env[model].sudo()
            
            # Ghi nhận log phục vụ kiểm tra
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info(f"API_RPC CALL: model={model}, method={method}, args={args}, kwargs={kwargs}")
            
            # Nếu method là action button (như action_gui_duyet hoặc read) và args[0] đại diện cho IDs
            if method not in ('create', 'search_read', 'search') and args:
                first_arg = args[0]
                while isinstance(first_arg, (list, tuple)) and first_arg and isinstance(first_arg[0], (list, tuple)):
                    first_arg = first_arg[0]
                
                if isinstance(first_arg, (list, tuple)):
                    ids = [x for x in first_arg if isinstance(x, int)]
                elif isinstance(first_arg, int):
                    ids = [first_arg]
                else:
                    ids = []
                
                if ids:
                    records = model_sudo.browse(ids)
                    _logger.info(f"API_RPC BROWSE: records={records}, calling method={method} with args={args[1:]}")
                    result = getattr(records, method)(*args[1:], **kwargs)
                    
                    from odoo import models
                    if isinstance(result, models.BaseModel):
                        return result.id if len(result) == 1 else result.ids
                    return result
            
            result = getattr(model_sudo, method)(*args, **kwargs)
            
            from odoo import models
            if isinstance(result, models.BaseModel):
                return result.id if len(result) == 1 else result.ids
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise ValidationError(str(e))

    # ── CORS preflight cho các API route ──────────────────────────
    @http.route([
        '/web/dataset/call_kw',
        '/web/session/authenticate',
        '/web/session/get_session_info',
        '/api/nhan_su/login',
        '/api/nhan_su/rpc',
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

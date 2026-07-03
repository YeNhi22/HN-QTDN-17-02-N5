# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, AccessDenied
import hashlib

# Cải tiến từ phiên bản cũ: Thêm phong_ban_id và chuc_vu_id trực tiếp vào model
# để các module Tài sản & Tài chính có thể đọc dữ liệu HRM mà không cần tra bảng
# lich_su_cong_tac mỗi lần → giảm query, tăng tốc đồng bộ.


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_ten'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho_ten = fields.Char("Họ tên", required=True, default='')
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    lich_su_cong_tac_ids = fields.One2many(
        "lich_su_cong_tac",
        string="Danh sách lịch sử công tác",
        inverse_name="nhan_vien_id"
    )
    tuoi = fields.Integer("Tuổi", compute="_compute_tuoi", store=True)

    # ================================================================
    # Cải tiến từ phiên bản cũ: Thêm 2 trường compute để các module
    # Tài sản & Tài chính đọc trực tiếp phòng ban / chức vụ hiện tại
    # của nhân viên mà không cần join qua bảng lich_su_cong_tac.
    # Đây là dữ liệu HRM gốc (Single Source of Truth) theo yêu cầu Mức 1.
    # ================================================================
    phong_ban_hien_tai_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban hiện tại',
        compute='_compute_phong_ban_chuc_vu_hien_tai',
        store=True,
        help='Phòng ban của nhân viên dựa trên lịch sử công tác gần nhất (dữ liệu HRM gốc)'
    )

    chuc_vu_hien_tai_id = fields.Many2one(
        'chuc_vu',
        string='Chức vụ hiện tại',
        compute='_compute_phong_ban_chuc_vu_hien_tai',
        store=True,
        help='Chức vụ của nhân viên dựa trên lịch sử công tác gần nhất (dữ liệu HRM gốc)'
    )
    # ================================================================

    # Liên kết với User Odoo (nếu có)
    user_id = fields.Many2one('res.users', string='Tài khoản Odoo', ondelete='set null')

    # Thông tin đăng nhập riêng cho web app bên ngoài
    web_username = fields.Char("Tên đăng nhập web")
    web_password_hash = fields.Char("Mật khẩu (hash)")
    is_web_active = fields.Boolean("Kích hoạt web", default=False)
    last_login = fields.Datetime("Đăng nhập lần cuối")

    @api.depends('ngay_sinh')
    def _compute_tuoi(self):
        for record in self:
            if record.ngay_sinh:
                record.tuoi = (fields.Date.today() - record.ngay_sinh).days // 365
            else:
                record.tuoi = 0

    # ================================================================
    # Cải tiến từ phiên bản cũ: Hàm compute lấy phòng ban & chức vụ
    # hiện tại từ bản ghi lịch sử công tác có time_end gần nhất (hoặc
    # mới nhất theo time_start nếu time_end bằng nhau).
    # store=True đảm bảo có thể filter/search theo phòng ban.
    # ================================================================
    @api.depends(
        'lich_su_cong_tac_ids',
        'lich_su_cong_tac_ids.phong_ban_id',
        'lich_su_cong_tac_ids.chuc_vu_id',
        'lich_su_cong_tac_ids.time_start',
        'lich_su_cong_tac_ids.time_end',
    )
    def _compute_phong_ban_chuc_vu_hien_tai(self):
        """
        Compute phòng ban và chức vụ hiện tại từ lịch sử công tác đang hiệu lực.
        Ưu tiên bản ghi có time_start <= hôm nay và time_end >= hôm nay (hoặc chưa kết thúc).
        """
        today = fields.Date.context_today(self)
        for record in self:
            active_lines = record.lich_su_cong_tac_ids.filtered(
                lambda r: r.time_start
                and r.time_start <= today
                and (not r.time_end or r.time_end >= today)
            )
            if active_lines:
                latest = active_lines.sorted(
                    key=lambda r: (r.time_start, r.time_end or today),
                    reverse=True,
                )[0]
            elif record.lich_su_cong_tac_ids:
                latest = record.lich_su_cong_tac_ids.sorted(
                    key=lambda r: r.time_start or today,
                    reverse=True,
                )[0]
            else:
                latest = False

            if latest:
                record.phong_ban_hien_tai_id = latest.phong_ban_id
                record.chuc_vu_hien_tai_id = latest.chuc_vu_id
            else:
                record.phong_ban_hien_tai_id = False
                record.chuc_vu_hien_tai_id = False

    def name_get(self):
        result = []
        for record in self:
            label = f"[{record.ma_dinh_danh}] {record.ho_ten}"
            if record.phong_ban_hien_tai_id:
                pb = record.phong_ban_hien_tai_id.ten_phong_ban \
                    or record.phong_ban_hien_tai_id.ma_phong_ban
                label = f"{label} — {pb}"
            result.append((record.id, label))
        return result

    def _hash_password(self, password):
        """Hash mật khẩu sử dụng SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @api.model
    def web_register(self, data):
        """Đăng ký tài khoản web mới"""
        try:
            existing = self.sudo().search([('web_username', '=', data.get('username'))], limit=1)
            if existing:
                return {'success': False, 'message': 'Tên đăng nhập đã tồn tại'}

            existing_employee = self.sudo().search([('ma_dinh_danh', '=', data.get('ma_dinh_danh'))], limit=1)
            if existing_employee:
                return {'success': False, 'message': 'Mã định danh đã tồn tại'}

            employee = self.sudo().create({
                'ma_dinh_danh': data.get('ma_dinh_danh'),
                'ho_ten': data.get('ho_ten'),
                'email': data.get('email'),
                'so_dien_thoai': data.get('so_dien_thoai'),
                'web_username': data.get('username'),
                'web_password_hash': self._hash_password(data.get('password', '')),
                'is_web_active': True,
            })

            return {
                'success': True,
                'message': 'Đăng ký thành công',
                'employee_id': employee.id,
                'employee': {
                    'id': employee.id,
                    'ma_dinh_danh': employee.ma_dinh_danh,
                    'ho_ten': employee.ho_ten,
                    'email': employee.email,
                }
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @api.model
    def web_login(self, username, password):
        """Đăng nhập cho web app bên ngoài"""
        try:
            password_hash = self._hash_password(password)
            employee = self.sudo().search([
                ('web_username', '=', username),
                ('web_password_hash', '=', password_hash),
                ('is_web_active', '=', True)
            ], limit=1)

            if not employee:
                return {'success': False, 'message': 'Tên đăng nhập hoặc mật khẩu không đúng'}

            employee.sudo().write({'last_login': fields.Datetime.now()})

            return {
                'success': True,
                'message': 'Đăng nhập thành công',
                'employee': {
                    'id': employee.id,
                    'ma_dinh_danh': employee.ma_dinh_danh,
                    'ho_ten': employee.ho_ten,
                    'email': employee.email,
                    'so_dien_thoai': employee.so_dien_thoai,
                    'tuoi': employee.tuoi,
                    # Cải tiến từ phiên bản cũ: Trả thêm phòng ban & chức vụ
                    'phong_ban': employee.phong_ban_hien_tai_id.ten_phong_ban if employee.phong_ban_hien_tai_id else None,
                    'chuc_vu': employee.chuc_vu_hien_tai_id.ten_chuc_vu if employee.chuc_vu_hien_tai_id else None,
                }
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @api.model
    def web_change_password(self, username, old_password, new_password):
        """Đổi mật khẩu"""
        try:
            old_hash = self._hash_password(old_password)
            employee = self.sudo().search([
                ('web_username', '=', username),
                ('web_password_hash', '=', old_hash),
            ], limit=1)

            if not employee:
                return {'success': False, 'message': 'Mật khẩu cũ không đúng'}

            employee.sudo().write({
                'web_password_hash': self._hash_password(new_password)
            })

            return {'success': True, 'message': 'Đổi mật khẩu thành công'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @api.model
    def get_employee_by_username(self, username):
        """Lấy thông tin nhân viên theo username"""
        employee = self.sudo().search([('web_username', '=', username)], limit=1)
        if not employee:
            return {'success': False, 'message': 'Không tìm thấy nhân viên'}

        return {
            'success': True,
            'employee': {
                'id': employee.id,
                'ma_dinh_danh': employee.ma_dinh_danh,
                'ho_ten': employee.ho_ten,
                'email': employee.email,
                'so_dien_thoai': employee.so_dien_thoai,
                'tuoi': employee.tuoi,
                'last_login': employee.last_login.isoformat() if employee.last_login else None,
                # Cải tiến từ phiên bản cũ: Trả thêm phòng ban & chức vụ hiện tại
                'phong_ban': employee.phong_ban_hien_tai_id.ten_phong_ban if employee.phong_ban_hien_tai_id else None,
                'chuc_vu': employee.chuc_vu_hien_tai_id.ten_chuc_vu if employee.chuc_vu_hien_tai_id else None,
            }
        }

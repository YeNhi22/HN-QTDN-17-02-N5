# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import json

# Cải tiến từ phiên bản cũ:
# 1. chi_phi_khau_hao: thêm hàm action_tinh_chi_phi_khau_hao() để tự động lấy
#    giá trị khấu hao từ module khau_hao_tai_san thay vì nhập tay.
# 2. Thêm phong_ban_id để lọc chi phí theo phòng ban từ dữ liệu HRM gốc.
# 3. Thêm @api.onchange tự điền chi phí khấu hao khi chọn tháng/năm/phòng ban.


class BaoCaoTaiChinh(models.Model):
    _name = 'bao_cao_tai_chinh'
    _description = 'Báo cáo tài chính'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'nam desc, thang desc'

    # ========== THÔNG TIN CHUNG ==========
    name = fields.Char(string='Tên báo cáo', required=True, copy=False)
    thang = fields.Integer(string='Tháng', required=True, default=lambda self: datetime.now().month)
    nam = fields.Integer(string='Năm', required=True, default=lambda self: datetime.now().year)

    # ================================================================
    # Cải tiến từ phiên bản cũ: Thêm phong_ban_id để lọc chi phí
    # theo phòng ban từ dữ liệu HRM. Khi chọn phòng ban, chi phí khấu hao
    # tự động lấy từ tài sản thuộc phòng ban đó.
    # ================================================================
    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban (lọc chi phí)',
        ondelete='set null',
        help='Chọn phòng ban để lọc chi phí khấu hao. Dữ liệu phòng ban từ HRM.'
    )

    # ========== TRẠNG THÁI ==========
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy')
    ], string='Trạng thái', default='draft', tracking=True)

    # ========== DOANH THU VÀ LỢI NHUẬN ==========
    doanh_thu = fields.Float(string='Doanh thu', default=0.0)
    tong_chi_phi = fields.Float(string='Tổng chi phí', compute='_compute_tong_chi_phi', store=True)
    loi_nhuan = fields.Float(string='Lợi nhuận', compute='_compute_loi_nhuan', store=True)
    ty_le_loi_nhuan = fields.Float(string='Tỷ lệ lợi nhuận (%)', compute='_compute_ty_le_loi_nhuan', store=True)

    # ========== CHI TIẾT CHI PHÍ ==========
    # Cải tiến từ phiên bản cũ: chi_phi_khau_hao vẫn là Float nhưng
    # có hàm _action_tu_dong_tinh_khau_hao() để tự fill từ KhauHaoTaiSan.
    chi_phi_khau_hao = fields.Float(string='Chi phí khấu hao', default=0.0)
    chi_phi_luong = fields.Float(string='Chi phí lương', default=0.0)
    chi_phi_van_phong = fields.Float(string='Chi phí văn phòng', default=0.0)
    chi_phi_marketing = fields.Float(string='Chi phí Marketing', default=0.0)
    chi_phi_dien_nuoc = fields.Float(string='Chi phí điện nước', default=0.0)
    chi_phi_khac = fields.Float(string='Chi phí khác', default=0.0)

    # ========== THÔNG TIN THEO DÕI ==========
    ngay_tao = fields.Datetime(string='Ngày tạo', default=fields.Datetime.now, readonly=True)
    ngay_hoan_thanh = fields.Datetime(string='Ngày hoàn thành', readonly=True)
    nguoi_tao_id = fields.Many2one('res.users', string='Người tạo', default=lambda self: self.env.user, readonly=True)
    nguoi_xu_ly_id = fields.Many2one('res.users', string='Người xử lý', readonly=True)

    # ========== DỮ LIỆU BIỂU ĐỒ ==========
    bieu_do_du_lieu = fields.Text(
        string='Dữ liệu biểu đồ', compute='_compute_bieu_do_du_lieu', store=False
    )
    bieu_do_phan_bo_chi_phi = fields.Text(
        string='Phân bổ chi phí', compute='_compute_bieu_do_phan_bo_chi_phi', store=False
    )

    # ========== COMPUTE METHODS ==========
    @api.depends('chi_phi_khau_hao', 'chi_phi_luong', 'chi_phi_van_phong',
                 'chi_phi_marketing', 'chi_phi_dien_nuoc', 'chi_phi_khac')
    def _compute_tong_chi_phi(self):
        for record in self:
            record.tong_chi_phi = (
                record.chi_phi_khau_hao +
                record.chi_phi_luong +
                record.chi_phi_van_phong +
                record.chi_phi_marketing +
                record.chi_phi_dien_nuoc +
                record.chi_phi_khac
            )

    @api.depends('doanh_thu', 'tong_chi_phi')
    def _compute_loi_nhuan(self):
        for record in self:
            record.loi_nhuan = record.doanh_thu - record.tong_chi_phi

    @api.depends('doanh_thu', 'loi_nhuan')
    def _compute_ty_le_loi_nhuan(self):
        for record in self:
            if record.doanh_thu > 0:
                record.ty_le_loi_nhuan = (record.loi_nhuan / record.doanh_thu) * 100
            else:
                record.ty_le_loi_nhuan = 0.0

    def _compute_bieu_do_du_lieu(self):
        for record in self:
            data = {
                'labels': ['Doanh thu', 'Tổng chi phí', 'Lợi nhuận'],
                'datasets': [{
                    'label': 'Triệu đồng',
                    'data': [
                        record.doanh_thu / 1000000,
                        record.tong_chi_phi / 1000000,
                        record.loi_nhuan / 1000000
                    ],
                    'backgroundColor': ['#28a745', '#dc3545', '#007bff']
                }]
            }
            record.bieu_do_du_lieu = json.dumps(data)

    def _compute_bieu_do_phan_bo_chi_phi(self):
        for record in self:
            labels = ['Khấu hao', 'Lương', 'Văn phòng', 'Marketing', 'Điện nước', 'Khác']
            data = [
                record.chi_phi_khau_hao, record.chi_phi_luong,
                record.chi_phi_van_phong, record.chi_phi_marketing,
                record.chi_phi_dien_nuoc, record.chi_phi_khac
            ]
            filtered_data, filtered_labels, filtered_colors = [], [], []
            colors = ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff', '#ff9f40']
            for i, value in enumerate(data):
                if value > 0:
                    filtered_data.append(value)
                    filtered_labels.append(labels[i])
                    filtered_colors.append(colors[i])
            record.bieu_do_phan_bo_chi_phi = json.dumps({
                'labels': filtered_labels,
                'datasets': [{'data': filtered_data, 'backgroundColor': filtered_colors, 'hoverOffset': 4}]
            })

    # ================================================================
    # Cải tiến từ phiên bản cũ: Thêm @api.onchange để khi người dùng
    # thay đổi tháng/năm hoặc phòng ban, hệ thống gợi ý tính chi phí
    # khấu hao tự động từ dữ liệu khau_hao_tai_san (tích hợp Asset→Finance).
    # ================================================================
    @api.onchange('thang', 'nam', 'phong_ban_id')
    def _onchange_tinh_ky_va_phong_ban(self):
        """
        Cải tiến từ phiên bản cũ: Khi chọn tháng/năm/phòng ban,
        tự động tính chi phí khấu hao từ dữ liệu khau_hao_tai_san.
        """
        if self.thang and self.nam:
            chi_phi = self._tinh_chi_phi_khau_hao_tu_module(self.thang, self.nam, self.phong_ban_id)
            if chi_phi > 0:
                self.chi_phi_khau_hao = chi_phi

    def _tinh_chi_phi_khau_hao_tu_module(self, thang, nam, phong_ban=False):
        """
        Cải tiến từ phiên bản cũ: Lấy chi phí khấu hao thực tế từ module
        khau_hao_tai_san thay vì nhập tay.

        Logic:
        - Lấy tất cả khấu hao đang hoạt động trong tháng/năm
        - Nếu có phòng ban: lọc thêm theo phòng ban của tài sản (HRM gốc)
        - Trả về tổng khấu hao tháng = sum(khau_hao_hang_nam) / 12
        """
        try:
            KhauHao = self.env['khau_hao_tai_san'].sudo()
            import datetime as dt
            ngay_dau_thang = dt.date(nam, thang, 1)

            domain = [
                ('ngay_bat_dau', '<=', ngay_dau_thang),
                ('trang_thai', '=', 'dang_khau_hao'),
            ]

            # Cải tiến từ phiên bản cũ: Lọc theo phòng ban HRM gốc
            if phong_ban:
                # Lấy tài sản thuộc phòng ban này (qua phong_ban_hien_tai_id compute)
                tai_san_ids = self.env['tai_san'].search([
                    ('phong_ban_hien_tai_id', '=', phong_ban.id)
                ]).ids
                if tai_san_ids:
                    domain.append(('tai_san_id', 'in', tai_san_ids))
                else:
                    return 0.0

            khau_hao_records = KhauHao.search(domain)
            tong_hang_nam = sum(khau_hao_records.mapped('gia_tri_khau_hao_hang_nam'))
            return round(tong_hang_nam / 12, 0) if tong_hang_nam else 0.0
        except Exception:
            return 0.0

    # ========== ACTION METHODS ==========
    def action_tinh_toan(self):
        """Tự động tính toán chi phí khấu hao từ module Asset và cập nhật báo cáo"""
        for record in self:
            # Cải tiến từ phiên bản cũ: Tự động lấy chi phí khấu hao từ
            # dữ liệu thực trong module quản_ly_tai_san thay vì giữ nguyên số cũ.
            chi_phi_kh = record._tinh_chi_phi_khau_hao_tu_module(
                record.thang, record.nam, record.phong_ban_id
            )
            record.write({
                'trang_thai': 'in_progress',
                'nguoi_xu_ly_id': self.env.user.id,
                'chi_phi_khau_hao': chi_phi_kh if chi_phi_kh > 0 else record.chi_phi_khau_hao,
            })
        return True

    def action_hoan_thanh(self):
        for record in self:
            record.write({
                'trang_thai': 'completed',
                'ngay_hoan_thanh': fields.Datetime.now()
            })
        return True

    def action_quay_lai_nhap(self):
        for record in self:
            record.write({'trang_thai': 'draft'})
        return True

    def action_huy(self):
        for record in self:
            record.write({'trang_thai': 'cancelled'})
        return True

    def action_in_bao_cao(self):
        return self.env.ref('quan_ly_tai_chinh.action_bao_cao_tai_chinh_pdf').report_action(self)

    def action_open_wizard_sao_chep(self):
        return {
            'name': 'Sao chép báo cáo',
            'type': 'ir.actions.act_window',
            'res_model': 'bao.cao.tai.chinh.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_bao_cao_id': self.id,
                'default_thang': self.thang,
                'default_nam': self.nam,
            }
        }

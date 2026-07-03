# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json
import logging

_logger = logging.getLogger(__name__)


class DashboardMain(models.TransientModel):
    """Dashboard Tổng quan - TransientModel để luôn tính toán mới"""
    _name = 'dashboard.main'
    _description = 'Dashboard Tổng quan'

    name = fields.Char('Tên', default='Dashboard', readonly=True)

    # Stats fields - computed
    total_tai_san = fields.Integer('Tổng tài sản', compute='_compute_stats', store=False)
    active_tai_san = fields.Integer('Đang sử dụng', compute='_compute_stats', store=False)
    dang_muon = fields.Integer('Đang cho mượn', compute='_compute_stats', store=False)
    don_cho_duyet = fields.Integer('Đơn chờ duyệt', compute='_compute_stats', store=False)
    qua_han = fields.Integer('Quá hạn', compute='_compute_stats', store=False)
    total_value = fields.Float('Tổng giá trị', compute='_compute_stats', store=False)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency')

    # HTML fields for display
    thong_bao_html = fields.Html('Thông báo', compute='_compute_thong_bao_html', sanitize=False)
    hoat_dong_html = fields.Html('Hoạt động', compute='_compute_hoat_dong_html', sanitize=False)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        TaiSan = self.env['tai_san']

        if 'total_tai_san' in fields_list:
            res['total_tai_san'] = TaiSan.search_count([])

        if 'active_tai_san' in fields_list:
            res['active_tai_san'] = TaiSan.search_count([
                ('trang_thai_thanh_ly', 'in', ['da_phan_bo', 'chua_phan_bo'])
            ])

        if 'total_value' in fields_list:
            tai_san_list = TaiSan.search([])
            res['total_value'] = sum(
                ts.gia_tri_hien_tai or ts.gia_tri_ban_dau or 0
                for ts in tai_san_list
            )

        try:
            DonMuon = self.env['don_muon_tai_san']
            if 'don_cho_duyet' in fields_list:
                res['don_cho_duyet'] = DonMuon.search_count([('trang_thai', '=', 'cho_duyet')])
            if 'dang_muon' in fields_list:
                res['dang_muon'] = DonMuon.search_count([('trang_thai', '=', 'dang_muon')])

            MuonTra = self.env['muon_tra_tai_san']
            if 'qua_han' in fields_list:
                res['qua_han'] = MuonTra.search_count([('trang_thai', '=', 'qua_han')])
        except Exception as e:
            _logger.warning("Error computing muon_tra stats in default_get: %s", e)
            for f in ['don_cho_duyet', 'dang_muon', 'qua_han']:
                if f in fields_list:
                    res[f] = 0

        # thong_bao_html
        if 'thong_bao_html' in fields_list:
            notifications = []
            don_cho = res.get('don_cho_duyet', 0)
            qua_han_count = res.get('qua_han', 0)
            if don_cho > 0:
                notifications.append({'icon': 'fa-clock-o', 'color': 'warning',
                                       'message': f'{don_cho} đơn mượn đang chờ duyệt'})
            if qua_han_count > 0:
                notifications.append({'icon': 'fa-exclamation-triangle', 'color': 'danger',
                                       'message': f'{qua_han_count} tài sản quá hạn chưa trả'})
            try:
                phe_duyet_cho = self.env['phe_duyet_mua_tai_san'].search_count([('state', '=', 'draft')])
                if phe_duyet_cho > 0:
                    notifications.append({'icon': 'fa-file-text-o', 'color': 'info',
                                          'message': f'{phe_duyet_cho} đề xuất mua chờ phê duyệt'})
            except Exception:
                pass

            if notifications:
                html = '<div class="list-group list-group-flush">'
                for notif in notifications:
                    bg = '#fff3cd' if notif['color'] == 'warning' else '#f8d7da' if notif['color'] == 'danger' else '#d1ecf1'
                    bd = '#ffc107' if notif['color'] == 'warning' else '#dc3545' if notif['color'] == 'danger' else '#17a2b8'
                    html += (
                        f'<div class="list-group-item d-flex align-items-center border-0" '
                        f'style="background:{bg};border-radius:10px;margin-bottom:8px;border-left:4px solid {bd} !important;">'
                        f'<i class="fa {notif["icon"]} mr-3"></i><span>{notif["message"]}</span></div>'
                    )
                html += '</div>'
                res['thong_bao_html'] = html
            else:
                res['thong_bao_html'] = (
                    '<div class="text-center py-4 text-muted">'
                    '<i class="fa fa-check-circle text-success fa-3x mb-2"></i>'
                    '<p>Không có thông báo mới</p></div>'
                )

        # hoat_dong_html
        if 'hoat_dong_html' in fields_list:
            activities = []
            try:
                DonMuon = self.env['don_muon_tai_san']
                recent_don = DonMuon.search([], limit=5, order='create_date desc')
                trang_thai_map = {
                    'nhap': ('Nháp', 'secondary'),
                    'cho_duyet': ('Chờ duyệt', 'warning'),
                    'da_duyet': ('Đã duyệt', 'success'),
                    'dang_muon': ('Đang mượn', 'warning'),
                    'da_tra': ('Đã trả', 'success'),
                    'tu_choi': ('Từ chối', 'danger'),
                    'huy': ('Đã hủy', 'secondary'),
                }
                for don in recent_don:
                    status = trang_thai_map.get(don.trang_thai, ('', 'secondary'))
                    ten_nv = don.nhan_vien_muon_id.ho_ten if don.nhan_vien_muon_id else 'N/A'
                    activities.append({
                        'icon': 'fa-file-text',
                        'color': status[1],
                        'title': f'Đơn mượn #{don.id}',
                        'desc': f'{ten_nv} - {status[0]}',
                        'date': don.create_date.strftime('%d/%m/%Y %H:%M') if don.create_date else '',
                    })
            except Exception as e:
                _logger.warning("Error getting recent activities: %s", e)

            if activities:
                html = '<div class="list-group list-group-flush">'
                for act in activities[:5]:
                    html += (
                        f'<div class="list-group-item d-flex align-items-center border-0 px-0">'
                        f'<div style="width:40px;height:40px;background:var(--{act["color"]},#6c757d);'
                        f'border-radius:10px;display:flex;align-items:center;justify-content:center;margin-right:15px;">'
                        f'<i class="fa {act["icon"]} text-white"></i></div>'
                        f'<div class="flex-grow-1"><div class="fw-bold">{act["title"]}</div>'
                        f'<small class="text-muted">{act["desc"]}</small></div>'
                        f'<small class="text-muted">{act["date"]}</small></div>'
                    )
                html += '</div>'
                res['hoat_dong_html'] = html
            else:
                res['hoat_dong_html'] = (
                    '<div class="text-center py-4 text-muted">'
                    '<i class="fa fa-inbox fa-3x mb-2"></i>'
                    '<p>Chưa có hoạt động nào</p></div>'
                )

        return res

    @api.depends_context('uid')
    def _compute_currency(self):
        for record in self:
            record.currency_id = self.env.company.currency_id

    @api.depends_context('uid')
    def _compute_stats(self):
        for record in self:
            TaiSan = self.env['tai_san']
            record.total_tai_san = TaiSan.search_count([])
            record.active_tai_san = TaiSan.search_count([
                ('trang_thai_thanh_ly', 'in', ['da_phan_bo', 'chua_phan_bo'])
            ])
            tai_san_list = TaiSan.search([])
            record.total_value = sum(
                ts.gia_tri_hien_tai or ts.gia_tri_ban_dau or 0 for ts in tai_san_list
            )
            try:
                DonMuon = self.env['don_muon_tai_san']
                record.don_cho_duyet = DonMuon.search_count([('trang_thai', '=', 'cho_duyet')])
                record.dang_muon = DonMuon.search_count([('trang_thai', '=', 'dang_muon')])
                MuonTra = self.env['muon_tra_tai_san']
                record.qua_han = MuonTra.search_count([
                    ('trang_thai', '=', 'qua_han'),
                ])
            except Exception as e:
                _logger.warning("Error computing stats: %s", e)
                record.don_cho_duyet = 0
                record.dang_muon = 0
                record.qua_han = 0

    @api.depends_context('uid')
    def _compute_thong_bao_html(self):
        for record in self:
            notifications = []
            if record.don_cho_duyet > 0:
                notifications.append({'icon': 'fa-clock-o', 'color': 'warning',
                                       'message': f'{record.don_cho_duyet} đơn mượn đang chờ duyệt'})
            if record.qua_han > 0:
                notifications.append({'icon': 'fa-exclamation-triangle', 'color': 'danger',
                                       'message': f'{record.qua_han} tài sản quá hạn chưa trả'})
            try:
                phe_duyet_cho = self.env['phe_duyet_mua_tai_san'].search_count([('state', '=', 'draft')])
                if phe_duyet_cho > 0:
                    notifications.append({'icon': 'fa-file-text-o', 'color': 'info',
                                          'message': f'{phe_duyet_cho} đề xuất mua chờ phê duyệt'})
            except Exception:
                pass

            if notifications:
                html = '<div class="list-group list-group-flush">'
                for notif in notifications:
                    bg = '#fff3cd' if notif['color'] == 'warning' else '#f8d7da' if notif['color'] == 'danger' else '#d1ecf1'
                    bd = '#ffc107' if notif['color'] == 'warning' else '#dc3545' if notif['color'] == 'danger' else '#17a2b8'
                    html += (
                        f'<div class="list-group-item d-flex align-items-center border-0" '
                        f'style="background:{bg};border-radius:10px;margin-bottom:8px;'
                        f'border-left:4px solid {bd} !important;">'
                        f'<i class="fa {notif["icon"]} mr-3" style="font-size:1.2rem;"></i>'
                        f'<span>{notif["message"]}</span></div>'
                    )
                html += '</div>'
                record.thong_bao_html = html
            else:
                record.thong_bao_html = (
                    '<div class="text-center py-4 text-muted">'
                    '<i class="fa fa-check-circle text-success fa-3x mb-2"></i>'
                    '<p>Không có thông báo mới</p></div>'
                )

    @api.depends_context('uid')
    def _compute_hoat_dong_html(self):
        for record in self:
            activities = []
            try:
                DonMuon = self.env['don_muon_tai_san']
                recent_don = DonMuon.search([], limit=5, order='create_date desc')
                trang_thai_map = {
                    'nhap': ('Nháp', 'secondary'),
                    'cho_duyet': ('Chờ duyệt', 'warning'),
                    'da_duyet': ('Đã duyệt', 'success'),
                    'dang_muon': ('Đang mượn', 'warning'),
                    'da_tra': ('Đã trả', 'success'),
                    'tu_choi': ('Từ chối', 'danger'),
                    'huy': ('Đã hủy', 'secondary'),
                }
                for don in recent_don:
                    status = trang_thai_map.get(don.trang_thai, ('', 'secondary'))
                    ten_nv = don.nhan_vien_muon_id.ho_ten if don.nhan_vien_muon_id else 'N/A'
                    activities.append({
                        'icon': 'fa-file-text',
                        'color': status[1],
                        'title': f'Đơn mượn #{don.id}',
                        'desc': f'{ten_nv} - {status[0]}',
                        'date': don.create_date.strftime('%d/%m/%Y %H:%M') if don.create_date else '',
                    })
            except Exception as e:
                _logger.warning("Error getting recent activities: %s", e)

            if activities:
                html = '<div class="list-group list-group-flush">'
                for act in activities[:5]:
                    html += (
                        f'<div class="list-group-item d-flex align-items-center border-0 px-0">'
                        f'<div style="width:40px;height:40px;background:var(--{act["color"]},#6c757d);'
                        f'border-radius:10px;display:flex;align-items:center;justify-content:center;margin-right:15px;">'
                        f'<i class="fa {act["icon"]} text-white"></i></div>'
                        f'<div class="flex-grow-1"><div class="fw-bold">{act["title"]}</div>'
                        f'<small class="text-muted">{act["desc"]}</small></div>'
                        f'<small class="text-muted">{act["date"]}</small></div>'
                    )
                html += '</div>'
                record.hoat_dong_html = html
            else:
                record.hoat_dong_html = (
                    '<div class="text-center py-4 text-muted">'
                    '<i class="fa fa-inbox fa-3x mb-2"></i>'
                    '<p>Chưa có hoạt động nào</p></div>'
                )

    # ============ ACTION BUTTONS ============
    def action_open_don_muon(self):
        return {'type': 'ir.actions.act_window', 'name': 'Đơn mượn tài sản',
                'res_model': 'don_muon_tai_san', 'view_mode': 'tree,form', 'target': 'current'}

    def action_open_muon_tra(self):
        return {'type': 'ir.actions.act_window', 'name': 'Quản lý mượn trả',
                'res_model': 'muon_tra_tai_san', 'view_mode': 'tree,form', 'target': 'current'}

    def action_open_tai_san(self):
        return {'type': 'ir.actions.act_window', 'name': 'Tài sản',
                'res_model': 'tai_san', 'view_mode': 'tree,form', 'target': 'current'}

    def action_open_kiem_ke(self):
        return {'type': 'ir.actions.act_window', 'name': 'Kiểm kê tài sản',
                'res_model': 'kiem_ke_tai_san', 'view_mode': 'tree,form', 'target': 'current'}

    def action_open_phe_duyet(self):
        return {'type': 'ir.actions.act_window', 'name': 'Phê duyệt mua tài sản',
                'res_model': 'phe_duyet_mua_tai_san', 'view_mode': 'tree,form', 'target': 'current'}

    def action_open_ocr(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'OCR Hóa đơn (Gemini AI)',
            'res_model': 'invoice.ocr.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_refresh_data(self):
        new_dashboard = self.create({'name': 'Dashboard'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dashboard Tổng quan',
            'res_model': 'dashboard.main',
            'view_mode': 'form',
            'res_id': new_dashboard.id,
            'view_id': self.env.ref('q_trang_chu.view_dashboard_main_form').id,
            'target': 'current',
        }

    # ============ API METHODS ============
    @api.model
    def get_dashboard_data(self):
        """API method trả về dữ liệu dashboard"""
        try:
            TaiSan = self.env['tai_san']
            total_tai_san = TaiSan.search_count([])
            active_tai_san = TaiSan.search_count([
                ('trang_thai_thanh_ly', 'in', ['da_phan_bo', 'chua_phan_bo'])
            ])
            tai_san_list = TaiSan.search([])
            total_value = sum(ts.gia_tri_hien_tai or ts.gia_tri_ban_dau or 0 for ts in tai_san_list)

            tai_chinh_data = {'tong_phe_duyet': 0, 'phe_duyet_cho_duyet': 0, 'tong_gia_tri_phe_duyet': 0}
            try:
                PheDuyet = self.env['phe_duyet_mua_tai_san']
                tai_chinh_data['tong_phe_duyet'] = PheDuyet.search_count([])
                tai_chinh_data['phe_duyet_cho_duyet'] = PheDuyet.search_count([('state', '=', 'draft')])
                tai_chinh_data['tong_gia_tri_phe_duyet'] = sum(
                    pd.tong_gia_tri or 0 for pd in PheDuyet.search([])
                )
            except Exception as e:
                _logger.warning("Error fetching financial data: %s", e)

            don_cho_duyet = dang_muon = qua_han = 0
            try:
                DonMuon = self.env['don_muon_tai_san']
                don_cho_duyet = DonMuon.search_count([('trang_thai', '=', 'cho_duyet')])
                dang_muon = DonMuon.search_count([('trang_thai', '=', 'dang_muon')])
                qua_han = self.env['muon_tra_tai_san'].search_count([
                    ('trang_thai', '=', 'qua_han'),
                ])
            except Exception as e:
                _logger.warning("Error computing muon_tra stats: %s", e)

            thong_bao = []
            if don_cho_duyet > 0:
                thong_bao.append({'icon': 'fa-clock-o', 'type': 'warning',
                                   'message': f'{don_cho_duyet} đơn mượn đang chờ duyệt'})
            if qua_han > 0:
                thong_bao.append({'icon': 'fa-exclamation-triangle', 'type': 'danger',
                                   'message': f'{qua_han} tài sản quá hạn chưa trả'})
            if tai_chinh_data['phe_duyet_cho_duyet'] > 0:
                thong_bao.append({'icon': 'fa-file-text-o', 'type': 'info',
                                   'message': f'{tai_chinh_data["phe_duyet_cho_duyet"]} đề xuất mua chờ phê duyệt'})

            hoat_dong_gan_day = []
            try:
                DonMuon = self.env['don_muon_tai_san']
                recent_don = DonMuon.search([], limit=5, order='create_date desc')
                trang_thai_map = {
                    'nhap': ('Nháp', 'secondary'), 'cho_duyet': ('Chờ duyệt', 'warning'),
                    'da_duyet': ('Đã duyệt', 'success'), 'dang_muon': ('Đang mượn', 'warning'),
                    'da_tra': ('Đã trả', 'success'), 'tu_choi': ('Từ chối', 'danger'),
                    'huy': ('Đã hủy', 'secondary'),
                }
                for don in recent_don:
                    status = trang_thai_map.get(don.trang_thai, ('', 'secondary'))
                    ten_nv = don.nhan_vien_muon_id.ho_ten if don.nhan_vien_muon_id else 'N/A'
                    hoat_dong_gan_day.append({
                        'icon': 'fa-file-text', 'color': status[1],
                        'title': f'Đơn mượn #{don.id}',
                        'description': f'{ten_nv} - {status[0]}',
                        'date': don.create_date.strftime('%d/%m/%Y %H:%M') if don.create_date else '',
                    })
            except Exception as e:
                _logger.warning("Error getting recent activities: %s", e)

            return {
                'tai_san': {'total': total_tai_san, 'active': active_tai_san,
                            'dang_muon': dang_muon, 'total_value': total_value, 'depreciated_value': 0},
                'tai_chinh': tai_chinh_data,
                'muon_tra': {'don_cho_duyet': don_cho_duyet, 'don_dang_muon': dang_muon, 'qua_han': qua_han},
                'thong_bao': thong_bao,
                'hoat_dong_gan_day': hoat_dong_gan_day,
            }
        except Exception as e:
            _logger.error("Error in get_dashboard_data: %s", e)
            return {
                'tai_san': {'total': 0, 'active': 0, 'dang_muon': 0, 'total_value': 0, 'depreciated_value': 0},
                'tai_chinh': {'tong_phe_duyet': 0, 'phe_duyet_cho_duyet': 0, 'tong_gia_tri_phe_duyet': 0},
                'muon_tra': {'don_cho_duyet': 0, 'don_dang_muon': 0, 'qua_han': 0},
                'thong_bao': [],
                'hoat_dong_gan_day': [],
            }

    @api.model
    def get_chart_data(self, chart_type):
        if chart_type == 'tai_san_theo_danh_muc':
            return self._get_assets_by_category()
        elif chart_type == 'muon_tra_theo_thang':
            return self._get_borrowing_by_month()
        return {}

    def _get_assets_by_category(self):
        result = []
        try:
            for dm in self.env['danh_muc_tai_san'].search([]):
                count = self.env['tai_san'].search_count([('danh_muc_ts_id', '=', dm.id)])
                if count > 0:
                    result.append({'name': dm.ten_danh_muc_ts, 'value': count})
        except Exception:
            pass
        return result

    def _get_borrowing_by_month(self):
        result = []
        try:
            DonMuon = self.env['don_muon_tai_san']
            for i in range(5, -1, -1):
                month_start = datetime.now().replace(day=1) - timedelta(days=i * 30)
                month_end = month_start + timedelta(days=30)
                count = DonMuon.search_count([
                    ('create_date', '>=', month_start),
                    ('create_date', '<', month_end),
                ])
                result.append({'month': month_start.strftime('%m/%Y'), 'count': count})
        except Exception:
            pass
        return result

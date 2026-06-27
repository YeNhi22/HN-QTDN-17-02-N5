# -*- coding: utf-8 -*-
import json
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

EVENT_TYPES = [
    ('hrm.department_changed', 'HRM: Phòng ban thay đổi'),
    ('de_xuat.submitted', 'Đề xuất mua: Đã gửi'),
    ('phe_duyet.approved', 'Phê duyệt: Đã duyệt'),
    ('phe_duyet.rejected', 'Phê duyệt: Từ chối'),
    ('don_muon.submitted', 'Đơn mượn: Đã gửi duyệt'),
    ('muon_tra.approved', 'Phiếu mượn trả: Đã duyệt'),
    ('muon_tra.borrowed', 'Phiếu mượn trả: Đã giao tài sản'),
    ('muon_tra.returned', 'Phiếu mượn trả: Đã trả'),
    ('khau_hao.calculated', 'Khấu hao: Đã tính toán'),
    ('khau_hao.posted', 'Khấu hao: Đã ghi sổ'),
]


class SystemEvent(models.Model):
    """
    Event Bus trung tâm (Mức 2 — Event-driven).
    Các module phát sự kiện; handler tự động thực thi tác vụ tiếp theo.
    """
    _name = 'system.event'
    _description = 'Sự kiện hệ thống'
    _order = 'create_date desc'

    name = fields.Char(string='Tên sự kiện', required=True)
    event_type = fields.Selection(EVENT_TYPES, string='Loại sự kiện', required=True, index=True)
    source_model = fields.Char(string='Model nguồn')
    source_id = fields.Integer(string='ID bản ghi nguồn')
    payload = fields.Text(string='Dữ liệu JSON')
    state = fields.Selection([
        ('pending', 'Chờ xử lý'),
        ('done', 'Hoàn thành'),
        ('failed', 'Lỗi'),
    ], string='Trạng thái', default='pending', required=True)
    result_message = fields.Text(string='Kết quả xử lý')
    handler_count = fields.Integer(string='Số handler', default=0)

    @api.model
    def emit(self, event_type, name, source_model=None, source_id=None, payload=None):
        """Phát sự kiện và tự động dispatch handler."""
        event = self.sudo().create({
            'name': name,
            'event_type': event_type,
            'source_model': source_model or False,
            'source_id': source_id or 0,
            'payload': json.dumps(payload or {}, ensure_ascii=False, default=str),
            'state': 'pending',
        })
        try:
            handlers_run = event._dispatch()
            event.write({
                'state': 'done',
                'handler_count': handlers_run,
                'result_message': _('Đã xử lý %s handler.') % handlers_run,
            })
        except Exception as exc:
            _logger.exception('System event dispatch failed: %s', event_type)
            event.write({
                'state': 'failed',
                'result_message': str(exc),
            })
        return event

    @api.model
    def safe_emit(self, event_type, name, source_model=None, source_id=None, payload=None):
        """Phát sự kiện an toàn — không làm gián đoạn transaction nghiệp vụ."""
        try:
            return self.emit(event_type, name, source_model, source_id, payload)
        except Exception as exc:
            _logger.warning('safe_emit failed for %s: %s', event_type, exc)
            return False

    def _get_payload(self):
        self.ensure_one()
        if not self.payload:
            return {}
        try:
            return json.loads(self.payload)
        except (json.JSONDecodeError, TypeError):
            return {}

    def _dispatch(self):
        """Chạy các handler theo loại sự kiện."""
        self.ensure_one()
        handlers = {
            'de_xuat.submitted': self._handle_de_xuat_submitted,
            'phe_duyet.approved': self._handle_phe_duyet_approved,
            'don_muon.submitted': self._handle_don_muon_submitted,
            'muon_tra.approved': self._handle_muon_tra_approved,
            'khau_hao.posted': self._handle_khau_hao_posted,
            'hrm.department_changed': self._handle_hrm_department_changed,
        }
        handler = handlers.get(self.event_type)
        if handler:
            handler()
            return 1
        return 0

    def _notify_external(self, message):
        """Gửi thông báo qua Telegram nếu module q_trang_chu đã cài."""
        try:
            service = self.env['telegram.notification.service']
        except KeyError:
            return
        try:
            service.send_message(message)
        except Exception as exc:
            _logger.warning('Telegram notification failed: %s', exc)

    def _handle_de_xuat_submitted(self):
        data = self._get_payload()
        msg = (
            f'📋 <b>Đề xuất mua mới</b>\n'
            f'Mã: {data.get("ma_de_xuat", "—")}\n'
            f'Tiêu đề: {data.get("ten_de_xuat", "—")}\n'
            f'Phòng ban: {data.get("phong_ban", "—")}\n'
            f'Tổng giá trị: {data.get("tong_gia_tri", 0):,.0f} VNĐ\n'
            f'→ Hệ thống đã tự động tạo đơn phê duyệt tài chính.'
        )
        self._notify_external(msg)

    def _handle_phe_duyet_approved(self):
        data = self._get_payload()
        msg = (
            f'✅ <b>Phê duyệt mua tài sản</b>\n'
            f'Mã: {data.get("ma_phe_duyet", "—")}\n'
            f'Đã tạo {data.get("so_tai_san", 0)} tài sản\n'
            f'Bút toán: {data.get("but_toan", "—")}\n'
            f'→ Luồng tự động: Tài sản + Sổ cái + Khấu hao hoàn tất.'
        )
        self._notify_external(msg)

    def _handle_don_muon_submitted(self):
        data = self._get_payload()
        msg = (
            f'📦 <b>Đơn mượn mới</b>\n'
            f'Mã: {data.get("ma_don_muon", "—")}\n'
            f'NV: {data.get("nhan_vien", "—")}\n'
            f'→ Hệ thống đã tự động tạo phiếu mượn trả.'
        )
        self._notify_external(msg)

    def _handle_muon_tra_approved(self):
        data = self._get_payload()
        msg = (
            f'✔️ <b>Phiếu mượn đã duyệt</b>\n'
            f'Mã phiếu: {data.get("ma_phieu", "—")}\n'
            f'NV: {data.get("nhan_vien", "—")}\n'
            f'Số TS: {data.get("so_tai_san", 0)}'
        )
        self._notify_external(msg)

    def _handle_khau_hao_posted(self):
        data = self._get_payload()
        msg = (
            f'💰 <b>Khấu hao tháng {data.get("thang_nam", "—")}</b>\n'
            f'Tổng: {data.get("tong_khau_hao", 0):,.0f} VNĐ\n'
            f'Bút toán: {data.get("but_toan", "—")}'
        )
        self._notify_external(msg)

    def _handle_hrm_department_changed(self):
        data = self._get_payload()
        msg = (
            f'👥 <b>HRM: Chuyển phòng ban</b>\n'
            f'NV: {data.get("nhan_vien", "—")}\n'
            f'{data.get("phong_ban_cu", "—")} → {data.get("phong_ban_moi", "—")}'
        )
        self._notify_external(msg)

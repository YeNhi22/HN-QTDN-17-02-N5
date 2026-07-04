# -*- coding: utf-8 -*-
"""
Email Notification Service – Nhóm 5
Gửi thông báo Gmail cho nhân viên khi có sự kiện liên quan đến tài sản.

Các sự kiện:
  1. Đơn mượn được phê duyệt  → nhân viên mượn
  2. Đơn mượn bị từ chối      → nhân viên mượn
  3. Đơn mượn được gửi duyệt  → xác nhận cho nhân viên
  4. Tài sản được phân bổ     → nhân viên được giao
  5. Nhắc quá hạn trả (cron)  → nhân viên đang mượn
"""
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class EmailNotificationService(models.AbstractModel):
    _name = 'email.notification.service'
    _description = 'Dịch vụ gửi thông báo Email cho nhân viên'

    @api.model
    def _get_employee_email(self, nhan_vien):
        """Lấy email của nhân viên (từ HRM)."""
        if not nhan_vien:
            return None
        return (nhan_vien.email or '').strip() or None

    @api.model
    def _send_email(self, to_email, subject, body_html, record=None):
        """
        Gửi email qua Odoo mail engine (dùng SMTP cấu hình trong Settings).
        Nếu chưa cấu hình SMTP thì tự động lưu vào hộp thư nội bộ Odoo.
        """
        if not to_email:
            _logger.warning('[EmailService] Bỏ qua: không có email người nhận')
            return False
        try:
            mail = self.env['mail.mail'].sudo().create({
                'subject': subject,
                'email_to': to_email,
                'body_html': body_html,
                'auto_delete': True,
                'state': 'outgoing',
            })
            mail.send()
            _logger.info(f'[EmailService] Đã gửi email tới {to_email}: {subject}')
            return True
        except Exception as e:
            _logger.error(f'[EmailService] Lỗi gửi email tới {to_email}: {e}')
            return False

    # ── Template helper ───────────────────────────────────────
    @api.model
    def _wrap_template(self, title, body, color='#1e3a5f'):
        return f"""
<div style="font-family:'Segoe UI',sans-serif;max-width:600px;margin:0 auto;
  background:#f8fafc;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0">
  <div style="background:{color};padding:20px 24px;color:white">
    <h2 style="margin:0;font-size:18px">🏢 Hệ thống Quản lý Tài sản</h2>
    <p style="margin:4px 0 0;font-size:13px;opacity:.85">Thông báo tự động – Nhóm 5</p>
  </div>
  <div style="padding:24px;background:white">
    <h3 style="color:{color};margin:0 0 16px">{title}</h3>
    {body}
  </div>
  <div style="background:#f1f5f9;padding:12px 24px;font-size:11px;color:#94a3b8;text-align:center">
    Email tự động từ hệ thống Odoo 15 · Nhóm 5 FIT-DNU 2026<br/>
    Vui lòng không trả lời email này.
  </div>
</div>"""

    # ═══════════════════════════════════════════════════════════
    # 1. Đơn mượn – Gửi duyệt thành công
    # ═══════════════════════════════════════════════════════════
    @api.model
    def notify_don_muon_gui_duyet(self, don_muon):
        nv = don_muon.nhan_vien_muon_id
        email = self._get_employee_email(nv)
        if not email:
            return
        tai_san_list = ''.join(
            f'<li>{line.phan_bo_tai_san_id.tai_san_id.ten_tai_san}</li>'
            for line in don_muon.don_muon_tai_san_ids
        ) or '<li>(Chưa có tài sản)</li>'
        body = f"""
<p>Xin chào <strong>{nv.ho_ten}</strong>,</p>
<p>Đơn mượn tài sản của bạn đã được gửi thành công và đang chờ phê duyệt.</p>
<table style="width:100%;border-collapse:collapse;font-size:13px;margin:12px 0">
  <tr><td style="padding:6px;color:#64748b;width:40%">Mã đơn mượn:</td>
      <td style="padding:6px;font-weight:600">{don_muon.ma_don_muon}</td></tr>
  <tr style="background:#f8fafc"><td style="padding:6px;color:#64748b">Tên đơn:</td>
      <td style="padding:6px">{don_muon.ten_don_muon}</td></tr>
  <tr><td style="padding:6px;color:#64748b">Thời gian mượn:</td>
      <td style="padding:6px">{str(don_muon.thoi_gian_muon)[:16] if don_muon.thoi_gian_muon else '–'}</td></tr>
  <tr style="background:#f8fafc"><td style="padding:6px;color:#64748b">Hạn trả:</td>
      <td style="padding:6px;color:#dc2626">{str(don_muon.thoi_gian_tra)[:16] if don_muon.thoi_gian_tra else '–'}</td></tr>
</table>
<p style="font-size:13px;color:#475569">Tài sản yêu cầu:</p>
<ul style="font-size:13px;color:#1e293b">{tai_san_list}</ul>
<p style="font-size:13px;color:#64748b">Bạn sẽ nhận được thông báo khi đơn được phê duyệt hoặc từ chối.</p>"""
        self._send_email(
            email,
            f'📋 Đơn mượn {don_muon.ma_don_muon} đã được gửi duyệt',
            self._wrap_template('Đơn mượn đã gửi thành công', body, '#1e3a5f')
        )

    # ═══════════════════════════════════════════════════════════
    # 2. Đơn mượn – Được phê duyệt
    # ═══════════════════════════════════════════════════════════
    @api.model
    def notify_don_muon_duyet(self, don_muon):
        nv = don_muon.nhan_vien_muon_id
        email = self._get_employee_email(nv)
        if not email:
            return
        body = f"""
<p>Xin chào <strong>{nv.ho_ten}</strong>,</p>
<div style="background:#d1fae5;border-left:4px solid #10b981;padding:12px 16px;
  border-radius:6px;margin:12px 0">
  <strong style="color:#065f46">✅ Đơn mượn của bạn đã được PHÊ DUYỆT!</strong>
</div>
<table style="width:100%;border-collapse:collapse;font-size:13px;margin:12px 0">
  <tr><td style="padding:6px;color:#64748b;width:40%">Mã đơn:</td>
      <td style="padding:6px;font-weight:600">{don_muon.ma_don_muon}</td></tr>
  <tr style="background:#f8fafc"><td style="padding:6px;color:#64748b">Tên đơn:</td>
      <td style="padding:6px">{don_muon.ten_don_muon}</td></tr>
  <tr><td style="padding:6px;color:#64748b">Hạn trả:</td>
      <td style="padding:6px;color:#dc2626;font-weight:600">
        {str(don_muon.thoi_gian_tra)[:16] if don_muon.thoi_gian_tra else '–'}</td></tr>
  <tr style="background:#f8fafc"><td style="padding:6px;color:#64748b">Người duyệt:</td>
      <td style="padding:6px">{don_muon.nguoi_duyet_id.name if don_muon.nguoi_duyet_id else '–'}</td></tr>
</table>
<p style="font-size:13px;color:#065f46;font-weight:500">
  → Vui lòng đến nhận tài sản tại phòng ban <strong>{don_muon.phong_ban_cho_muon_id.ten_phong_ban}</strong>.
</p>
<p style="font-size:12px;color:#94a3b8">Lưu ý: Nhớ trả đúng hạn để tránh bị ghi nhận vi phạm.</p>"""
        self._send_email(
            email,
            f'✅ Đơn mượn {don_muon.ma_don_muon} đã được phê duyệt',
            self._wrap_template('Đơn mượn được phê duyệt', body, '#10b981')
        )

    # ═══════════════════════════════════════════════════════════
    # 3. Đơn mượn – Bị từ chối
    # ═══════════════════════════════════════════════════════════
    @api.model
    def notify_don_muon_tu_choi(self, don_muon, ly_do=''):
        nv = don_muon.nhan_vien_muon_id
        email = self._get_employee_email(nv)
        if not email:
            return
        body = f"""
<p>Xin chào <strong>{nv.ho_ten}</strong>,</p>
<div style="background:#fee2e2;border-left:4px solid #ef4444;padding:12px 16px;
  border-radius:6px;margin:12px 0">
  <strong style="color:#991b1b">❌ Đơn mượn của bạn đã bị TỪ CHỐI.</strong>
</div>
<table style="width:100%;border-collapse:collapse;font-size:13px;margin:12px 0">
  <tr><td style="padding:6px;color:#64748b;width:40%">Mã đơn:</td>
      <td style="padding:6px;font-weight:600">{don_muon.ma_don_muon}</td></tr>
  <tr style="background:#f8fafc"><td style="padding:6px;color:#64748b">Tên đơn:</td>
      <td style="padding:6px">{don_muon.ten_don_muon}</td></tr>
  <tr><td style="padding:6px;color:#64748b">Lý do từ chối:</td>
      <td style="padding:6px;color:#dc2626">{ly_do or 'Không có lý do cụ thể'}</td></tr>
</table>
<p style="font-size:13px;color:#475569">
  Bạn có thể tạo đơn mượn mới hoặc liên hệ quản lý để biết thêm thông tin.
</p>"""
        self._send_email(
            email,
            f'❌ Đơn mượn {don_muon.ma_don_muon} bị từ chối',
            self._wrap_template('Đơn mượn bị từ chối', body, '#ef4444')
        )

    # ═══════════════════════════════════════════════════════════
    # 4. Phân bổ tài sản mới cho nhân viên
    # ═══════════════════════════════════════════════════════════
    @api.model
    def notify_phan_bo_tai_san(self, phan_bo):
        nv = phan_bo.nhan_vien_su_dung_id
        email = self._get_employee_email(nv)
        if not email:
            return
        ts = phan_bo.tai_san_id
        body = f"""
<p>Xin chào <strong>{nv.ho_ten}</strong>,</p>
<p>Bạn vừa được phân bổ một tài sản mới từ hệ thống.</p>
<div style="background:#dbeafe;border-left:4px solid #3b82f6;padding:16px;
  border-radius:8px;margin:12px 0">
  <p style="margin:0 0 8px;font-size:15px;font-weight:700;color:#1e40af">
    📦 {ts.ten_tai_san}
  </p>
  <p style="margin:0;font-size:12px;color:#3b82f6">Mã: {ts.ma_tai_san}</p>
</div>
<table style="width:100%;border-collapse:collapse;font-size:13px;margin:12px 0">
  <tr><td style="padding:6px;color:#64748b;width:40%">Loại tài sản:</td>
      <td style="padding:6px">{ts.danh_muc_ts_id.ten_danh_muc_ts if ts.danh_muc_ts_id else '–'}</td></tr>
  <tr style="background:#f8fafc"><td style="padding:6px;color:#64748b">Giá trị hiện tại:</td>
      <td style="padding:6px">{ts.gia_tri_hien_tai:,.0f} VNĐ</td></tr>
  <tr><td style="padding:6px;color:#64748b">Ngày phân bổ:</td>
      <td style="padding:6px">{str(phan_bo.ngay_phat)}</td></tr>
  <tr style="background:#f8fafc"><td style="padding:6px;color:#64748b">Phòng ban:</td>
      <td style="padding:6px">{phan_bo.phong_ban_id.ten_phong_ban if phan_bo.phong_ban_id else '–'}</td></tr>
</table>
<p style="font-size:13px;color:#475569">
  Vui lòng sử dụng tài sản đúng mục đích và báo cáo ngay khi có sự cố.
</p>"""
        self._send_email(
            email,
            f'📦 Bạn được phân bổ tài sản: {ts.ten_tai_san}',
            self._wrap_template('Phân bổ tài sản mới', body, '#3b82f6')
        )

    # ═══════════════════════════════════════════════════════════
    # 5. Cron: Nhắc nhở sắp quá hạn trả (chạy hàng ngày)
    # ═══════════════════════════════════════════════════════════
    @api.model
    def cron_notify_sap_qua_han(self):
        """Gửi email nhắc nhở cho nhân viên sắp quá hạn trả (trong 1-2 ngày tới)."""
        from datetime import timedelta
        now = fields.Datetime.now()
        deadline = now + timedelta(days=2)
        don_muons = self.env['don_muon_tai_san'].sudo().search([
            ('trang_thai', '=', 'dang_muon'),
            ('thoi_gian_tra', '>=', now),
            ('thoi_gian_tra', '<=', deadline),
        ])
        count = 0
        for dm in don_muons:
            nv = dm.nhan_vien_muon_id
            email = self._get_employee_email(nv)
            if not email:
                continue
            con_lai = dm.thoi_gian_tra - now
            so_gio = int(con_lai.total_seconds() / 3600)
            if so_gio < 24:
                canh_bao = f'<span style="color:#dc2626;font-weight:700">⚠️ Còn {so_gio} giờ!</span>'
            else:
                so_ngay = con_lai.days
                canh_bao = f'<span style="color:#f59e0b;font-weight:700">⏰ Còn {so_ngay} ngày</span>'

            tai_san_list = ''.join(
                f'<li>{line.phan_bo_tai_san_id.tai_san_id.ten_tai_san}</li>'
                for line in dm.don_muon_tai_san_ids
            )
            body = f"""
<p>Xin chào <strong>{nv.ho_ten}</strong>,</p>
<div style="background:#fef3c7;border-left:4px solid #f59e0b;padding:12px 16px;
  border-radius:6px;margin:12px 0">
  <strong>⏰ Nhắc nhở: Sắp đến hạn trả tài sản!</strong>
</div>
<table style="width:100%;border-collapse:collapse;font-size:13px;margin:12px 0">
  <tr><td style="padding:6px;color:#64748b;width:40%">Mã đơn:</td>
      <td style="padding:6px;font-weight:600">{dm.ma_don_muon}</td></tr>
  <tr style="background:#f8fafc"><td style="padding:6px;color:#64748b">Hạn trả:</td>
      <td style="padding:6px">{str(dm.thoi_gian_tra)[:16]} – {canh_bao}</td></tr>
  <tr><td style="padding:6px;color:#64748b">Phòng ban trả:</td>
      <td style="padding:6px">{dm.phong_ban_cho_muon_id.ten_phong_ban}</td></tr>
</table>
<p style="font-size:13px;color:#475569">Tài sản cần trả:</p>
<ul style="font-size:13px;color:#1e293b">{tai_san_list}</ul>
<p style="font-size:13px;color:#dc2626;font-weight:500">
  Vui lòng trả tài sản đúng hạn để tránh vi phạm quy định.
</p>"""
            self._send_email(
                email,
                f'⏰ Nhắc nhở: Sắp hết hạn trả tài sản – {dm.ma_don_muon}',
                self._wrap_template('Nhắc nhở hạn trả tài sản', body, '#f59e0b')
            )
            count += 1
        _logger.info(f'[Cron] Đã gửi {count} email nhắc nhở quá hạn')
        return count

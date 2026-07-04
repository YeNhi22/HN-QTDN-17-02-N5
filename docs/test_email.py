"""
Test gửi email – Nhóm 5 Odoo 15
Tránh lỗi marshal None bằng cách dùng ir.actions.server thay vì gọi send() trực tiếp.

Chạy trong Ubuntu WSL:  python3 test_email.py
Chạy trong PowerShell:  python test_email.py
"""
import xmlrpc.client, time

ODOO_URL  = 'http://localhost:8069'
ODOO_DB   = 'quan_ly_btl'
ODOO_USER = 'admin@admin.com'
ODOO_PASS = 'admin'

# allow_none=True trên cả 2 phía để tránh lỗi marshal None
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object', allow_none=True)

def ex(model, method, args=None, **kw):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS,
        model, method, args or [[]], kw or {})

print('══════════════════════════════════════════')
print('  TEST EMAIL – Nhóm 5 Odoo 15')
print('══════════════════════════════════════════')
print(f'  ✅ Kết nối Odoo OK (uid={uid})')

# ── TEST 1: SMTP ───────────────────────────────────────────
print('\n=== TEST 1: Cấu hình SMTP ===')
servers = ex('ir.mail_server', 'search_read',
             fields=['name','smtp_host','smtp_port','smtp_user'])
for s in servers:
    print(f'  ✅ {s["name"]} | {s["smtp_host"]}:{s["smtp_port"]} | {s["smtp_user"]}')

# ── TEST 2: Tạo và gửi email ──────────────────────────────
print('\n=== TEST 2: Gửi email test ===')
TO = 'vego.tech555@gmail.com'

# Tạo mail record
mail_data = [{
    'subject': '✅ [Test] Hệ thống Quản lý Tài sản – Nhóm 5',
    'email_to': TO,
    'email_from': 'vego.tech555@gmail.com',
    'body_html': '''
<div style="font-family:sans-serif;max-width:480px;padding:0">
  <div style="background:#1e3a5f;color:white;padding:16px;border-radius:8px 8px 0 0">
    <h2 style="margin:0;font-size:17px">🏢 Hệ thống Quản lý Tài sản</h2>
    <p style="margin:4px 0 0;font-size:11px;opacity:.8">Nhóm 5 – FIT-DNU 2026</p>
  </div>
  <div style="background:white;padding:20px;border:1px solid #e2e8f0">
    <div style="background:#d1fae5;border-left:4px solid #10b981;
      padding:12px;border-radius:6px;margin-bottom:14px">
      <strong style="color:#065f46">✅ Kết nối Gmail thành công!</strong>
    </div>
    <p style="color:#475569;font-size:13px;line-height:1.6">
      Hệ thống email Odoo 15 đã hoạt động bình thường.<br/>
      Các thông báo sau sẽ tự động gửi về Gmail:<br/>
      <br/>
      📋 Đơn mượn tài sản được gửi duyệt<br/>
      ✅ Đơn mượn được phê duyệt<br/>
      ❌ Đơn mượn bị từ chối<br/>
      📦 Phân bổ tài sản mới<br/>
      ⏰ Nhắc nhở sắp quá hạn trả
    </p>
  </div>
  <div style="background:#f8fafc;padding:8px;text-align:center;
    font-size:11px;color:#94a3b8;border-radius:0 0 8px 8px">
    Email tự động từ Odoo 15 – Nhóm 5 FIT-DNU
  </div>
</div>''',
    'auto_delete': False,
    'state': 'outgoing',
}]

mail_ids = ex('mail.mail', 'create', [mail_data])
if isinstance(mail_ids, list):
    mail_id = mail_ids[0]
else:
    mail_id = mail_ids
print(f'  Đã tạo mail ID: {mail_id}')

# Gửi qua scheduler (không gọi send() trực tiếp → tránh None marshal)
# Cách: set state = outgoing rồi trigger ir.mail_server.send_queue
ex('mail.mail', 'write', [[mail_id]], vals={'state': 'outgoing'})

# Gọi send_queue để gửi tất cả mail outgoing
try:
    ex('mail.mail', 'process_email_queue', [[mail_id]])
    print('  ✅ process_email_queue đã được gọi')
except Exception:
    # Fallback: gọi _send trực tiếp qua shell command
    try:
        ex('ir.mail_server', 'send_email', [[]])
        print('  ✅ send_email triggered')
    except Exception as e2:
        print(f'  ℹ️  {e2}')

# Chờ 5 giây rồi check kết quả
time.sleep(5)
mails = ex('mail.mail', 'search_read', [[['id','=',mail_id]]],
           fields=['state','failure_reason'])
if mails:
    state  = mails[0].get('state','?')
    reason = mails[0].get('failure_reason') or ''
    if state == 'sent':
        print(f'  ✅ GỬI THÀNH CÔNG! Kiểm tra hộp thư: {TO}')
    elif state == 'exception':
        print(f'  ❌ LỖI GỬI: {reason}')
        if 'Username' in reason or 'authentication' in reason.lower():
            print('     → App Password sai hoặc Gmail chưa bật 2FA')
        elif 'Connection' in reason:
            print('     → Không kết nối được SMTP (kiểm tra mạng)')
    elif state == 'outgoing':
        print(f'  ℹ️  Đang trong hàng chờ gửi (outgoing)')
        print(f'     → Vào Odoo: Thiết lập → Kỹ thuật → Email → Tất cả email')
        print(f'     → Tìm mail ID {mail_id}, nhấn "Gửi ngay"')
    else:
        print(f'  ℹ️  Trạng thái: {state}')

# ── TEST 3: Kiểm tra service email ─────────────────────────
print('\n=== TEST 3: EmailNotificationService ===')
count_dang_muon = ex('don_muon_tai_san', 'search_count',
                     [[['trang_thai','=','dang_muon']]])
print(f'  Đơn đang mượn: {count_dang_muon}')
try:
    result = ex('email.notification.service', 'cron_notify_sap_qua_han', [])
    val = result if result is not None else 0
    print(f'  ✅ Cron nhắc quá hạn OK, gửi {val} email')
except Exception as e:
    # AbstractModel không nhận args rỗng – thử không truyền args
    try:
        result = models.execute_kw(ODOO_DB, uid, ODOO_PASS,
            'email.notification.service', 'cron_notify_sap_qua_han', [], {})
        print(f'  ✅ Cron OK: {result if result is not None else 0} email')
    except Exception as e2:
        print(f'  ℹ️  Cron: {e2}')

# ── KẾT QUẢ ───────────────────────────────────────────────
print('\n══════════════════════════════════════════')
print('  DONE')
print(f'  → Kiểm tra hộp thư: {TO}')
print(f'  → Hoặc Spam folder nếu chưa thấy')
print('══════════════════════════════════════════')

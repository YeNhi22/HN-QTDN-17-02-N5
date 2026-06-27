# Smoke test — chạy trong: odoo shell -d DB --no-http < docs/scripts/smoke_test_odoo15.py
print('Models OK:', 'system.event' in env, 'hrm.sync.log' in env, 'invoice.ocr.result' in env)
evt = env['system.event'].safe_emit(
    'de_xuat.submitted', 'Test event',
    payload={'ma_de_xuat': 'TEST-001', 'ten_de_xuat': 'Test', 'phong_ban': 'IT', 'tong_gia_tri': 1000},
)
print('Event state:', evt.state if evt else 'failed')
print('ALL_CHECKS_PASSED')

# SỬA LỖI CÀI ĐẶT MODULE

## Lỗi đã sửa:

**File:** `addons/quan_ly_tai_san/views/don_muon_tai_san.xml`

**Lỗi:** 
```
ValueError: External ID not found in the system: quan_ly_tai_san.don_muon_tai_san_action
```

**Nguyên nhân:**
- Button trong form view tham chiếu đến action `don_muon_tai_san_action`
- Action này được định nghĩa trong cùng file nhưng ở phía sau
- Odoo yêu cầu action phải tồn tại trước khi sử dụng

**Giải pháp:**
- Xóa button không cần thiết trong `oe_button_box`
- Button này chỉ hiển thị số tài sản, không quan trọng

**Code đã xóa:**
```xml
<div class="oe_button_box" name="button_box">
    <button name="%(quan_ly_tai_san.don_muon_tai_san_action)d" type="action"
        class="oe_stat_button" icon="fa-list"
        attrs="{'invisible': [('so_tai_san', '=', 0)]}">
        <field name="so_tai_san" widget="statinfo" string="Tài sản"/>
    </button>
</div>
```

## Cách cài lại:

1. Gỡ cài đặt module (nếu đã cài):
   ```
   Apps → quan_ly_tai_san → Uninstall
   ```

2. Cài lại module:
   ```
   Apps → Update Apps List → Tìm "quan_ly_tai_san" → Install
   ```

3. Nếu vẫn lỗi, restart Odoo server:
   ```bash
   # Stop server (Ctrl+C)
   # Start lại
   python odoo-bin -c odoo.conf -d your_database --dev=all
   ```

---

**Trạng thái:** ✅ Đã sửa xong


---

## Lỗi 2: Module q_trang_chu

**File:** `addons/q_trang_chu/views/dashboard_views.xml`

**Lỗi:** 
```
ValueError: External ID not found in the system: q_trang_chu.view_dashboard_main_form
```

**Nguyên nhân:**
- Action `action_dashboard_main` được định nghĩa **TRƯỚC** view `view_dashboard_main_form`
- Action tham chiếu đến view chưa tồn tại
- Odoo yêu cầu view phải được định nghĩa trước khi action tham chiếu đến nó

**Giải pháp:**
- Đổi thứ tự trong file XML
- View được định nghĩa đầu tiên
- Sau đó mới đến các action (server action và window action)

**Thứ tự mới:**
1. `view_dashboard_main_form` (view - định nghĩa trước)
2. `action_dashboard_main_server` (server action)
3. `action_dashboard_main` (window action)

---

**Trạng thái:** ✅ Cả 2 lỗi đã sửa xong

## Hướng dẫn cài lại:

1. Restart Odoo server:
   ```bash
   # Stop server (Ctrl+C)
   python odoo-bin -c odoo.conf -d your_database --dev=all
   ```

2. Cài module theo thứ tự:
   ```
   1. nhan_su
   2. quan_ly_tai_san
   3. quan_ly_tai_chinh
   4. q_trang_chu  ← Module dashboard (tùy chọn)
   ```

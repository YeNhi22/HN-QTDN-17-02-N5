# 🎨 UI COMPONENTS GUIDE

**Hệ thống Design System** cho Odoo 15 ERP Premium

---

## 📊 MÀU SẮC CHỦ ĐẠO

### 🟣 Nhân sự (HRM)
```css
Primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Ý nghĩa: Chuyên nghiệp, đáng tin cậy
```

### 🔴 Tài sản (Assets)
```css
Primary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)
Ý nghĩa: Năng động, quản lý tài sản
```

### 🟢 Tài chính (Finance)
```css
Primary: linear-gradient(135deg, #11998e 0%, #38ef7d 100%)
Ý nghĩa: Tăng trưởng, tài chính ổn định
```

### 🌈 Dashboard
```css
Multi-gradient: #667eea, #764ba2, #f093fb, #4facfe
Animated: 15s smooth transition
```

---

## 🎯 COMPONENTS LIBRARY

### 1. CARDS (Thẻ)

#### 📋 Glassmorphism Card
**Mô tả**: Card trong suốt với hiệu ứng kính mờ

**HTML Example**:
```xml
<div class="o_form_sheet">
    <!-- Nội dung tự động có glassmorphism -->
</div>
```

**CSS**:
```css
background: rgba(255, 255, 255, 0.95);
backdrop-filter: blur(10px);
border-radius: 24px;
box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
```

**Khi nào dùng**: Form views, Detail pages

---

#### 💳 Stats Card
**Mô tả**: Card hiển thị thống kê với icon và số liệu

**HTML Example**:
```xml
<div class="o_stat_card primary">
    <div class="o_stat_icon primary">
        <i class="fa fa-users"/>
    </div>
    <div class="o_stat_value">150</div>
    <div class="o_stat_label">TOTAL USERS</div>
</div>
```

**Variants**:
- `.primary` - Tím gradient
- `.success` - Xanh lá
- `.warning` - Hồng
- `.info` - Xanh dương

**Khi nào dùng**: Dashboard, Overview pages

---

### 2. BUTTONS (Nút)

#### ⚡ Primary Button
**Mô tả**: Nút chính với gradient

**Classes**:
- `.o_form_button_save` - Nút Lưu
- `.o_form_button_create` - Nút Tạo
- `.btn-primary` - Nút chung

**Effects**:
- Hover: Lift up + Glow
- Active: Scale down
- Gradient background

---

#### 🎯 Action Buttons
**Mô tả**: Nút thao tác nhanh

**HTML Example**:
```xml
<button name="action_approve" 
        type="object" 
        class="o_form_button_approve">
    <i class="fa fa-check"/> Approve
</button>
```

**Variants**:
- `.o_form_button_approve` - Xanh lá (Duyệt)
- `.o_form_button_reject` - Đỏ (Từ chối)
- `.o_quick_action_btn` - Quick actions

---

### 3. INPUTS (Trường nhập)

#### 📥 Text Input
**Features**:
- Border 2px solid #e8e8e8
- Border-radius: 12px
- Focus: Border xanh + Shadow glow
- Padding: 12px 16px

**Auto-applied**: Tất cả input, select, textarea

---

#### 📅 Date Input
**Features**:
- Icon lịch bên trái
- Format: dd/mm/yyyy
- Datepicker dropdown

---

#### 💰 Monetary Input
**Features**:
- Gradient text
- Prefix "VND"
- Large font-size
- Bold weight

---

### 4. BADGES & TAGS

#### 🏷️ Status Badge
**Mô tả**: Hiển thị trạng thái

**HTML Example**:
```xml
<span class="badge badge-success">Đã duyệt</span>
<span class="badge badge-warning">Chờ duyệt</span>
<span class="badge badge-danger">Từ chối</span>
```

**Styles**:
- Border-radius: 20px
- Padding: 6px 14px
- Font-weight: 600
- Box-shadow: Glow effect

---

#### 🎯 Many2many Tags
**Mô tả**: Tags có thể xóa được

**Auto-styled**: `.o_field_many2manytags`

**Features**:
- Gradient background
- Close button (×)
- Hover effect

---

### 5. TABLES (Bảng)

#### 📊 List View Table
**Features**:
- Header gradient
- Row hover: Scale + Shadow
- Rounded corners
- Glassmorphism background

**Auto-applied**: `.o_list_view table`

---

#### 💼 Finance Report Table
**Mô tả**: Bảng báo cáo tài chính

**Class**: `.o_finance_report_table`

**Features**:
- Bold header
- Hover highlight
- Currency formatting
- Total row emphasized

---

### 6. NAVIGATION

#### 📌 Tabs
**Mô tả**: Navigation tabs

**Features**:
- Inactive: White + Border
- Active: Gradient + White text
- Hover: Light background
- Border-radius: 12px 12px 0 0

**Auto-applied**: `.o_notebook .nav-tabs`

---

#### 🔍 Search Panel
**Features**:
- Glassmorphism card
- Category labels bold
- Active highlight
- Smooth transitions

**Auto-applied**: `.o_search_panel`

---

### 7. PROGRESS & CHARTS

#### 📈 Progress Bar
**HTML Example**:
```xml
<div class="o_progressbar">
    <div class="o_progressbar_value" style="width: 75%;"></div>
</div>
```

**Features**:
- Height: 12px
- Border-radius: 24px
- Gradient fill
- Animated width transition

---

#### 💹 Budget Progress
**Class**: `.o_finance_budget_bar`

**Features**:
- Large height: 40px
- Percentage label
- Over-budget warning
- Smooth animation

---

### 8. ALERTS & NOTIFICATIONS

#### 🔔 Alert Box
**HTML Example**:
```xml
<div class="o_asset_alert warning">
    <i class="fa fa-exclamation-triangle"></i>
    <span>Tài sản quá hạn bảo trì</span>
</div>
```

**Variants**:
- `.warning` - Vàng
- `.danger` - Đỏ
- `.info` - Xanh dương
- `.success` - Xanh lá

**Features**:
- Gradient background
- Border-left accent
- Icon prominent
- Shadow

---

#### 📢 Finance Alert
**Class**: `.o_finance_alert`

**Variants**:
- `.over_budget` - Vượt ngân sách (đỏ)
- `.under_budget` - Trong ngân sách (xanh)

---

### 9. SPECIAL COMPONENTS

#### 🖼️ Avatar
**Features**:
- Border-radius: 50%
- Border: 4px white
- Box-shadow
- Hover: Scale

**Auto-applied**: `.o_field_image`

---

#### 📷 Image Gallery
**Class**: `.o_asset_image_gallery`

**Features**:
- Grid layout
- Aspect ratio 1:1
- Hover scale
- Rounded corners

---

#### 💬 Timeline
**Mô tả**: Hiển thị lịch sử

**Class**: `.o_activity_timeline`

**Features**:
- Vertical line
- Circle icons
- Hover expand
- Date stamps

---

### 10. ANIMATIONS

#### ✨ Entrance Animations
```css
fadeInUp    - Card hiện từ dưới lên (0.6s)
slideInDown - Header trượt xuống (0.8s)
slideInLeft - Trượt từ trái (0.5s)
slideInRight - Trượt từ phải (0.5s)
scaleIn     - Phóng to (0.6s)
```

**Usage**: Auto-applied cho cards, rows

---

#### 🔄 Hover Animations
```css
translateY(-8px)  - Nâng lên
scale(1.05)       - Phóng to nhẹ
rotateY(360deg)   - Xoay 360°
```

**Usage**: Cards, Buttons, Icons

---

#### 🌟 Continuous Animations
```css
gradientShift  - Background animation (15s)
float          - Particles (20s)
pulse          - Nhấp nháy (1.5s)
shimmer        - Loading effect (2s)
financeGlow    - Glow effect (2s)
```

---

## 🎯 USAGE EXAMPLES

### Example 1: Form View với Glassmorphism

```xml
<form string="Employee" class="o_hrm_form">
    <sheet>
        <div class="oe_title">
            <h1>
                <field name="name"/>
            </h1>
        </div>
        
        <group>
            <group>
                <field name="employee_code"/>
                <field name="email" widget="email"/>
                <field name="phone" widget="phone"/>
            </group>
            <group>
                <field name="department_id"/>
                <field name="job_id"/>
                <field name="date_join"/>
            </group>
        </group>
        
        <notebook>
            <page string="Thông tin">
                <field name="history_ids"/>
            </page>
        </notebook>
    </sheet>
</form>
```

**Result**: Form tự động có glassmorphism, tabs gradient, fields neumorphism

---

### Example 2: Dashboard Stats

```xml
<div class="o_dashboard_stats">
    <div class="o_stat_card primary">
        <div class="o_stat_icon primary">
            <i class="fa fa-users"/>
        </div>
        <div class="o_stat_value">
            <field name="total_employees"/>
        </div>
        <div class="o_stat_label">
            <i class="fa fa-database"/> TOTAL EMPLOYEES
        </div>
    </div>
    
    <!-- More stats... -->
</div>
```

**Result**: Stats cards với animation staggered

---

### Example 3: Approval Buttons

```xml
<header>
    <button name="action_submit" 
            states="draft" 
            type="object" 
            class="btn-primary">
        <i class="fa fa-paper-plane"/> Submit
    </button>
    
    <button name="action_approve" 
            states="submitted" 
            type="object" 
            class="o_form_button_approve">
        <i class="fa fa-check"/> Approve
    </button>
    
    <button name="action_reject" 
            states="submitted" 
            type="object" 
            class="o_form_button_reject">
        <i class="fa fa-times"/> Reject
    </button>
</header>
```

**Result**: Buttons với gradient và hover effects

---

## 📋 CHEATSHEET

### Quick Reference

| Component | Class | Color |
|-----------|-------|-------|
| HRM Card | `.o_hrm_form` | Tím |
| Asset Card | `.o_asset_form` | Hồng |
| Finance Card | `.o_finance_form` | Xanh lá |
| Primary Button | `.btn-primary` | Gradient |
| Success Badge | `.badge-success` | Xanh lá |
| Warning Badge | `.badge-warning` | Vàng |
| Stat Card | `.o_stat_card` | Theo variant |
| Alert | `.o_alert` | Theo type |

---

## 🎨 CUSTOMIZATION

### Thay đổi màu chủ đạo

```css
/* File: custom.css */
:root {
    --hrm-primary: linear-gradient(135deg, #YOUR_COLOR_1, #YOUR_COLOR_2);
}
```

### Thay đổi border-radius

```css
/* Toàn bộ cards */
.o_form_sheet {
    border-radius: 32px !important; /* Từ 24px */
}
```

### Tắt animations

```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation: none !important;
        transition: none !important;
    }
}
```

---

## 📱 RESPONSIVE CLASSES

| Class | Breakpoint | Behavior |
|-------|------------|----------|
| `.col-md-*` | 768px | 2 columns on tablet |
| `.col-sm-*` | 576px | 1 column on mobile |
| `.d-none.d-md-block` | 768px | Hide on mobile |

---

**Tổng số components**: 50+  
**Browser support**: Chrome 76+, Firefox 70+, Safari 14+  
**Performance**: GPU-accelerated animations

---

**© 2026 Premium UI Design System** ✨

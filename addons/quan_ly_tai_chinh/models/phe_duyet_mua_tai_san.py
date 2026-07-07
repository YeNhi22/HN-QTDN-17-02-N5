# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

_logger = logging.getLogger(__name__)

class PheDuyetMuaTaiSan(models.Model):
    """
    Model phê duyệt mua tài sản - Bước 2 trong luồng mua thiết bị
    Nhận đơn từ module tài sản → Phê duyệt → Tự động tạo tài sản + ghi nhận tài chính
    """
    _name = 'phe_duyet_mua_tai_san'
    _description = 'Phê duyệt mua tài sản'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ma_phe_duyet'
    _order = 'ngay_tao desc'

    # ============ THÔNG TIN CƠ BẢN ============
    ma_phe_duyet = fields.Char(
        string='Mã phê duyệt',
        required=True,
        readonly=True,
        copy=False,
        default='New',
        tracking=True,
        help='Mã tự động tạo khi lưu đơn phê duyệt'
    )
    
    ngay_tao = fields.Date(
        string='Ngày tạo',
        default=fields.Date.context_today,
        required=True,
        readonly=True,
        tracking=True
    )
    
    # ============ LIÊN KẾT ĐỀ XUẤT GỐC ============
    de_xuat_mua_id = fields.Many2one(
        'de_xuat_mua_tai_san',
        string='Đề xuất mua',
        required=False,  # ← Thay đổi thành False để tránh lỗi
        readonly=True,
        ondelete='set null',  # ← Thay đổi để tránh lỗi restrict
        tracking=True,
        help='Đề xuất mua tài sản từ module quản lý tài sản'
    )
    
    ma_de_xuat = fields.Char(
        string='Mã đề xuất',
        compute='_compute_ma_de_xuat',
        readonly=True,
        store=False,
        help='Mã đề xuất gốc (nếu có)'
    )
    
    # ============ THÔNG TIN TỪ ĐỀ XUẤT ============
    ten_de_xuat = fields.Char(
        string='Tiêu đề',
        readonly=True,
        tracking=True
    )
    
    ngay_de_xuat = fields.Date(
        string='Ngày đề xuất',
        readonly=True
    )
    
    nguoi_de_xuat_id = fields.Many2one(
        'res.users',
        string='Người đề xuất',
        readonly=True,
        ondelete='set null'
    )

    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên đề xuất (HRM)',
        readonly=True,
        ondelete='set null',
        help='Dữ liệu gốc từ module HRM',
    )
    
    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban đề xuất',
        readonly=True,
        ondelete='set null'
    )
    
    # ============ CHI TIẾT THIẾT BỊ ============
    line_ids = fields.One2many(
        'phe_duyet_mua_tai_san.line',
        'phe_duyet_id',
        string='Chi tiết thiết bị',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    # ============ TỔNG TIỀN ============
    tong_gia_tri = fields.Float(
        string='Tổng giá trị',
        readonly=True,
        tracking=True
    )
    
    don_vi_tien_te = fields.Selection([
        ('vnd', 'VNĐ'),
        ('usd', 'USD'),
    ], string='Đơn vị tiền tệ', readonly=True)
    
    # ============ LÝ DO VÀ MÔ TẢ ============
    ly_do = fields.Text(
        string='Lý do đề xuất',
        readonly=True
    )
    
    mo_ta = fields.Html(
        string='Mô tả chi tiết',
        readonly=True
    )
    
    ngay_du_kien_nhan = fields.Date(
        string='Ngày dự kiến nhận hàng',
        readonly=True
    )
    
    # ============ TRẠNG THÁI ============
    state = fields.Selection([
        ('draft', 'Chờ phê duyệt'),
        ('approved', 'Đã phê duyệt'),
        ('rejected', 'Từ chối'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    # ============ PHÊ DUYỆT ============
    nguoi_phe_duyet_id = fields.Many2one(
        'res.users',
        string='Người phê duyệt',
        readonly=True,
        tracking=True,
        ondelete='set null'
    )
    
    ngay_phe_duyet = fields.Date(
        string='Ngày phê duyệt',
        readonly=True,
        tracking=True
    )
    
    ghi_chu_phe_duyet = fields.Text(
        string='Ghi chú phê duyệt',
        tracking=True
    )
    
    # ============ TÀI CHÍNH ============
    # Tài khoản kế toán
    tk_tai_san_id = fields.Many2one(
        'account.account',
        string='TK Tài sản cố định',
        domain="[('deprecated', '=', False)]",
        help='Tài khoản ghi Nợ khi mua tài sản (VD: 211 - TSCĐ hữu hình)',
        ondelete='restrict'
    )
    
    tk_nguon_von_id = fields.Many2one(
        'account.account',
        string='TK Nguồn vốn',
        domain="[('deprecated', '=', False)]",
        help='Tài khoản ghi Có khi mua tài sản (VD: 112 - Tiền mặt, 1121 - Tiền gửi ngân hàng)',
        ondelete='restrict'
    )
    
    journal_id = fields.Many2one(
        'account.journal',
        string='Sổ nhật ký',
        help='Sổ nhật ký ghi nhận giao dịch mua tài sản',
        ondelete='restrict'
    )
    
    # Bút toán đã tạo
    but_toan_id = fields.Many2one(
        'account.move',
        string='Bút toán ghi nhận',
        readonly=True,
        tracking=True,
        help='Bút toán ghi nhận mua tài sản',
        ondelete='set null'
    )
    
    # Liên kết đến bảng quản trị tài chính (nếu có)
    tai_khoan_quan_tri_ids = fields.One2many(
        'tai_khoan_quan_tri',
        'phe_duyet_mua_id',
        string='Ghi nhận quản trị',
        readonly=True
    )
    
    # ============ TÀI SẢN ĐÃ TẠO ============
    tai_san_ids = fields.Many2many(
        'tai_san',
        string='Tài sản đã tạo',
        readonly=True,
        help='Danh sách tài sản được tạo sau khi phê duyệt'
    )
    
    tai_san_count = fields.Integer(
        string='Số lượng tài sản',
        compute='_compute_tai_san_count'
    )
    
    # ============ KHẤU HAO ============
    khau_hao_ids = fields.One2many(
        'khau_hao_tai_san',
        'phe_duyet_mua_id',
        string='Lịch khấu hao',
        readonly=True,
        help='Lịch khấu hao tự động cho các tài sản'
    )
    
    # ============ COMPUTE METHODS ============
    @api.depends('de_xuat_mua_id', 'de_xuat_mua_id.ma_de_xuat')
    def _compute_ma_de_xuat(self):
        """
        Compute mã đề xuất an toàn, tránh lỗi _unknown
        
        Xử lý:
        - Kiểm tra de_xuat_mua_id tồn tại
        - Kiểm tra record có exists() không
        - Xử lý exception khi truy cập thuộc tính
        - Luôn gán giá trị (False nếu không có)
        """
        for record in self:
            try:
                # Kiểm tra 1: de_xuat_mua_id có giá trị không
                if not record.de_xuat_mua_id:
                    record.ma_de_xuat = False
                    continue
                
                # Kiểm tra 2: Record có tồn tại trong DB không
                if not record.de_xuat_mua_id.exists():
                    record.ma_de_xuat = False
                    continue
                
                # Kiểm tra 3: Truy cập an toàn thuộc tính ma_de_xuat
                ma = record.de_xuat_mua_id.ma_de_xuat
                record.ma_de_xuat = ma if ma else False
                
            except AttributeError:
                # Nếu gặp lỗi AttributeError (_unknown object)
                record.ma_de_xuat = False
            except Exception:
                # Bất kỳ exception nào khác
                record.ma_de_xuat = False
    
    @api.depends('tai_san_ids')
    def _compute_tai_san_count(self):
        for record in self:
            record.tai_san_count = len(record.tai_san_ids)
    
    # ============ ONCHANGE METHODS ============
    @api.onchange('de_xuat_mua_id')
    def _onchange_de_xuat_mua_id(self):
        """
        Xử lý khi thay đổi đề xuất mua
        Đảm bảo không gây lỗi _unknown object
        """
        # Không làm gì nếu không có đề xuất
        if not self.de_xuat_mua_id:
            return
        
        # Kiểm tra đề xuất có tồn tại không
        if not self.de_xuat_mua_id.exists():
            self.de_xuat_mua_id = False
            return
        
        # Trigger recompute cho ma_de_xuat
        # Field sẽ tự động compute an toàn qua _compute_ma_de_xuat
        pass
    
    # ============ CRUD METHODS ============
    @api.model_create_multi
    def create(self, vals_list):
        self.env['sequence.helper'].assign_codes_multi(
            vals_list, 'ma_phe_duyet', 'phe_duyet_mua_tai_san', 'PDTS', 'phe_duyet_mua_tai_san'
        )
        # Xử lý an toàn các trường Many2one - đảm bảo không có giá trị invalid
        many2one_fields = ['de_xuat_mua_id', 'nguoi_de_xuat_id', 'phong_ban_id', 
                           'nguoi_phe_duyet_id', 'tk_tai_san_id', 'tk_nguon_von_id', 
                           'journal_id', 'but_toan_id']
        
        for vals in vals_list:
            for field_name in many2one_fields:
                if field_name in vals:
                    field_value = vals[field_name]
                    # Nếu là False, None, hoặc 0 thì set về False
                    if not field_value or field_value == 0:
                        vals[field_name] = False
                    # Nếu là tuple (command), giữ nguyên
                    elif isinstance(field_value, (list, tuple)):
                        continue
                    # Nếu là int, kiểm tra record có tồn tại không
                    elif isinstance(field_value, int):
                        field_obj = self._fields[field_name]
                        if hasattr(field_obj, 'comodel_name'):
                            model_name = field_obj.comodel_name
                            if model_name and model_name in self.env:
                                if not self.env[model_name].browse(field_value).exists():
                                    vals[field_name] = False
            
            # Xử lý line_ids an toàn
            if 'line_ids' in vals:
                safe_lines = []
                for line_cmd in vals['line_ids']:
                    if isinstance(line_cmd, (list, tuple)) and len(line_cmd) >= 3:
                        cmd, _, line_vals = line_cmd[0], line_cmd[1], line_cmd[2] if len(line_cmd) > 2 else {}
                        if cmd == 0 and isinstance(line_vals, dict):
                            # Xử lý an toàn danh_muc_ts_id trong line
                            if 'danh_muc_ts_id' in line_vals:
                                dm_val = line_vals['danh_muc_ts_id']
                                if not dm_val or dm_val == 0:
                                    line_vals['danh_muc_ts_id'] = False
                                elif isinstance(dm_val, int):
                                    if 'danh_muc_tai_san' in self.env:
                                        if not self.env['danh_muc_tai_san'].browse(dm_val).exists():
                                            line_vals['danh_muc_ts_id'] = False
                        safe_lines.append(line_cmd)
                vals['line_ids'] = safe_lines
        
        return super(PheDuyetMuaTaiSan, self).create(vals_list)
    
    @api.model
    def default_get(self, fields_list):
        """Thiết lập giá trị mặc định cho tài khoản"""
        res = super(PheDuyetMuaTaiSan, self).default_get(fields_list)
        if 'ma_phe_duyet' in fields_list:
            res['ma_phe_duyet'] = self.env['sequence.helper'].get_default_code(
                'phe_duyet_mua_tai_san', 'ma_phe_duyet', 'phe_duyet_mua_tai_san', 'PDTS'
            )
        
        # Tài khoản tài sản cố định mặc định (211)
        if 'tk_tai_san_id' in fields_list:
            tk_ts = self.env['account.account'].search([
                ('code', '=like', '211%'),
                ('deprecated', '=', False)
            ], limit=1)
            if tk_ts:
                res['tk_tai_san_id'] = tk_ts.id
        
        # Tài khoản tiền mặt mặc định (112)
        if 'tk_nguon_von_id' in fields_list:
            tk_tien = self.env['account.account'].search([
                ('code', '=like', '112%'),
                ('deprecated', '=', False)
            ], limit=1)
            if tk_tien:
                res['tk_nguon_von_id'] = tk_tien.id
        
        # Sổ nhật ký mặc định — ưu tiên Nhật ký chung (ít ràng buộc nhất)
        if 'journal_id' in fields_list:
            journal = self.env['account.journal'].search([
                ('type', '=', 'general')
            ], limit=1)
            if not journal:
                journal = self.env['account.journal'].search([
                    ('type', '=', 'purchase')
                ], limit=1)
            if journal:
                res['journal_id'] = journal.id
        
        return res

    def _resolve_accounting_for_approval(self):
        """Tự động tìm hoặc tạo tài khoản kế toán 211/112 trước khi phê duyệt."""
        self.ensure_one()

        vals = {}

        try:
            # ---- Sổ nhật ký ----
            if not self.journal_id:
                journal = self.env['account.journal'].search(
                    [('type', 'in', ['general', 'purchase'])], limit=1
                )
                if not journal:
                    journal = self.env['account.journal'].search([], limit=1)
                if journal:
                    vals['journal_id'] = journal.id

            # ---- TK Tài sản cố định (211) ----
            if not self.tk_tai_san_id:
                tk_ts = self.env['account.account'].search([
                    ('deprecated', '=', False),
                    ('code', '=like', '211%'),
                ], limit=1)
                if not tk_ts:
                    # Tìm loại tài khoản phù hợp nhất
                    user_type = (
                        self.env.ref('account.data_account_type_fixed_assets', raise_if_not_found=False)
                        or self.env['account.account.type'].search([('type', '=', 'other')], limit=1)
                        or self.env['account.account.type'].search([], limit=1)
                    )
                    if user_type:
                        tk_ts = self.env['account.account'].sudo().create({
                            'code': '211',
                            'name': 'Tài sản cố định hữu hình',
                            'user_type_id': user_type.id,
                            'reconcile': False,
                        })
                if tk_ts:
                    vals['tk_tai_san_id'] = tk_ts.id

            # ---- TK Nguồn vốn (112) ----
            if not self.tk_nguon_von_id:
                tk_nv = self.env['account.account'].search([
                    ('deprecated', '=', False),
                    '|', ('code', '=like', '112%'), ('code', '=like', '111%'),
                ], limit=1)
                if not tk_nv:
                    user_type = (
                        self.env.ref('account.data_account_type_liquidity', raise_if_not_found=False)
                        or self.env['account.account.type'].search([('type', '=', 'liquidity')], limit=1)
                        or self.env['account.account.type'].search([], limit=1)
                    )
                    if user_type:
                        tk_nv = self.env['account.account'].sudo().create({
                            'code': '112',
                            'name': 'Tiền gửi ngân hàng',
                            'user_type_id': user_type.id,
                            'reconcile': False,
                        })
                if tk_nv:
                    vals['tk_nguon_von_id'] = tk_nv.id

            if vals:
                self.write(vals)

        except Exception as e:
            # Nếu không tạo được tài khoản → bỏ qua, phê duyệt vẫn chạy
            import logging
            logging.getLogger(__name__).warning(
                "Không tạo được tài khoản kế toán, bỏ qua bút toán: %s", e
            )
    
    # ============ ACTION METHODS ============
    def action_approve(self):
        """Phê duyệt đơn mua tài sản"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Chỉ có thể phê duyệt đơn đang chờ phê duyệt.'))

            record.flush()
            record._resolve_accounting_for_approval()
            
            # Cập nhật trạng thái
            record.write({
                'state': 'approved',
                'nguoi_phe_duyet_id': self.env.user.id,
                'ngay_phe_duyet': fields.Date.today(),
            })
            
            # ===== BƯỚC 1: TẠO TÀI SẢN TRONG MODULE QUẢN LÝ TÀI SẢN =====
            # Cải tiến từ phiên bản cũ: XÓA self.env.cr.commit() thủ công.
            # Odoo tự động commit khi toàn bộ transaction kết thúc thành công.
            # Đây là bước QUAN TRỌNG NHẤT - phải thành công
            created_assets = False
            try:
                created_assets = record._create_assets()
                # Cải tiến từ phiên bản cũ: Bỏ self.env.cr.commit() - vi phạm ACID
                # Odoo sẽ tự động commit khi method kết thúc không có exception
            except Exception as e:
                # Nếu không tạo được tài sản, raise exception để Odoo tự động rollback
                # Cải tiến từ phiên bản cũ: Bỏ self.env.cr.rollback() - Odoo tự xử lý
                raise UserError(_('Lỗi khi tạo tài sản trong module quản lý tài sản:\n%s\n\nVui lòng kiểm tra:\n- Module Quản lý tài sản đã được cài đặt\n- Danh mục tài sản đã được thiết lập\n- Các trường bắt buộc đã đầy đủ') % str(e))
            
            # ===== BƯỚC 2: GHI NHẬN TÀI CHÍNH (SỔ CÁI) =====
            # Cải tiến từ phiên bản cũ: Bỏ self.env.cr.commit() thủ công
            # Tạo bút toán kế toán
            try:
                record._create_journal_entry()
                # Cải tiến từ phiên bản cũ: Bỏ self.env.cr.commit() - vi phạm ACID
            except Exception as e:
                # Nếu gặp lỗi, chỉ log warning
                record.message_post(
                    body=_('Cảnh báo: Không tạo được bút toán kế toán. Lỗi: %s\nTài sản đã được tạo thành công.') % str(e),
                    subject=_('Cảnh báo bút toán')
                )
            
            # ===== BƯỚC 3: TẠO LỊCH KHẤU HAO =====
            # Cải tiến từ phiên bản cũ: Bỏ self.env.cr.commit() thủ công
            try:
                record._create_depreciation_schedule()
                # Cải tiến từ phiên bản cũ: Bỏ self.env.cr.commit() - vi phạm ACID
            except Exception as e:
                # Log lỗi nhưng tiếp tục
                record.message_post(
                    body=_('Cảnh báo: Không tạo được lịch khấu hao. Lỗi: %s\nBạn có thể tạo khấu hao thủ công sau.') % str(e),
                    subject=_('Cảnh báo khấu hao')
                )
            
            # ===== BƯỚC 4: GHI NHẬN KẾ TOÁN QUẢN TRỊ =====
            # Cải tiến từ phiên bản cũ: Bỏ self.env.cr.commit() thủ công
            try:
                record._create_management_accounting()
                # Cải tiến từ phiên bản cũ: Bỏ self.env.cr.commit() - vi phạm ACID
            except Exception as e:
                # Log lỗi nhưng tiếp tục
                record.message_post(
                    body=_('Cảnh báo: Không ghi nhận được vào kế toán quản trị. Lỗi: %s') % str(e),
                    subject=_('Cảnh báo kế toán quản trị')
                )
            
            # ===== BƯỚC 5: CẬP NHẬT ĐỀ XUẤT GỐC =====
            # Cải tiến từ phiên bản cũ: Bỏ self.env.cr.commit() thủ công
            try:
                if record.de_xuat_mua_id and record.de_xuat_mua_id.exists():
                    record.de_xuat_mua_id._on_approval_approved()
                    # Đồng bộ tài sản vào đề xuất
                    if created_assets:
                        record.de_xuat_mua_id.write({'tai_san_ids': [(6, 0, created_assets.ids)]})
                    # Cải tiến từ phiên bản cũ: Bỏ self.env.cr.commit() - vi phạm ACID
            except Exception as e:
                # Bỏ qua nếu không thể cập nhật đề xuất
                record.message_post(
                    body=_('Cảnh báo: Không cập nhật được đề xuất gốc. Lỗi: %s') % str(e),
                    subject=_('Cảnh báo đề xuất')
                )
            
            # ===== HOÀN THÀNH =====
            record.write({'state': 'done'})
            # Cải tiến từ phiên bản cũ: Bỏ self.env.cr.commit() cuối cùng
            # Odoo tự động commit toàn bộ transaction khi method kết thúc thành công
            
            # Gửi thông báo thành công
            asset_count = len(created_assets) if created_assets else 0
            record.message_post(
                body=_('✅ Phê duyệt thành công!\n\n'
                       '📦 Đã tạo %s tài sản trong module Quản lý tài sản\n'
                       '💰 Đã ghi nhận giao dịch vào hệ thống tài chính\n'
                       '📊 Tài sản sẵn sàng cho: Tính khấu hao, Kiểm kê, Mượn trả, Thanh lý, Bảo trì') % asset_count,
                subject=_('Phê duyệt hoàn tất')
            )

            self.env['system.event'].safe_emit(
                'phe_duyet.approved',
                f'Phê duyệt {record.ma_phe_duyet} hoàn tất',
                source_model='phe_duyet_mua_tai_san',
                source_id=record.id,
                payload={
                    'ma_phe_duyet': record.ma_phe_duyet,
                    'so_tai_san': asset_count,
                    'but_toan': record.but_toan_id.name if record.but_toan_id else '—',
                    'tong_gia_tri': record.tong_gia_tri,
                },
            )
    
    def action_reject(self):
        """Từ chối đơn mua tài sản"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Chỉ có thể từ chối đơn đang chờ phê duyệt.'))
            
            record.write({
                'state': 'rejected',
                'nguoi_phe_duyet_id': self.env.user.id,
                'ngay_phe_duyet': fields.Date.today(),
            })
            
            # Cập nhật trạng thái đề xuất gốc
            if record.de_xuat_mua_id and record.de_xuat_mua_id.exists():
                try:
                    record.de_xuat_mua_id._on_approval_rejected()
                except:
                    pass  # Bỏ qua nếu không thể cập nhật đề xuất
            
            # Gửi thông báo
            record.message_post(
                body=_('Đơn mua tài sản đã bị từ chối.'),
                subject=_('Đơn bị từ chối')
            )
    
    def action_cancel(self):
        """Hủy đơn phê duyệt"""
        for record in self:
            if record.state in ['approved', 'done']:
                raise UserError(_('Không thể hủy đơn đã được phê duyệt hoàn thành.'))
            record.state = 'cancelled'
    
    def unlink(self):
        """
        Xóa đơn phê duyệt
        Khi xóa, cần reset trạng thái đề xuất gốc về draft để có thể xóa
        """
        for record in self:
            # Gọi callback ở module tài sản để reset trạng thái
            if record.de_xuat_mua_id and record.de_xuat_mua_id.exists():
                try:
                    record.de_xuat_mua_id._on_approval_deleted()
                except Exception as e:
                    _logger.warning(
                        "Could not reset proposal %s: %s",
                        record.de_xuat_mua_id.id, e,
                    )
        
        return super(PheDuyetMuaTaiSan, self).unlink()
    
    def _create_assets(self):
        """
        Tự động tạo tài sản trong module quản lý tài sản
        
        Luồng:
        1. Kiểm tra module quản_ly_tai_san đã cài đặt
        2. Tạo tài sản theo từng dòng chi tiết
        3. Mỗi dòng tạo nhiều tài sản theo số lượng
        4. Lưu liên kết tài sản vào đơn phê duyệt
        5. Đồng bộ tài sản về đề xuất gốc
        
        Returns:
            recordset: Danh sách tài sản đã tạo (tai_san)
        """
        self.ensure_one()
        
        # Kiểm tra module quản lý tài sản
        if not self.env['ir.module.module'].search([
            ('name', '=', 'quan_ly_tai_san'), 
            ('state', '=', 'installed')
        ]):
            raise UserError(_('Module Quản lý tài sản chưa được cài đặt.\n\nVui lòng cài đặt module "quan_ly_tai_san" trước khi phê duyệt mua tài sản.'))
        
        # Kiểm tra có chi tiết thiết bị không
        if not self.line_ids:
            raise UserError(_('Không có chi tiết thiết bị nào để tạo tài sản.\n\nVui lòng thêm thiết bị vào đơn phê duyệt.'))
        
        tai_san_obj = self.env['tai_san']
        created_assets = self.env['tai_san']

        # ── Tìm danh mục mặc định để dùng khi line không có danh mục ────
        danh_muc_mac_dinh = self.env['danh_muc_tai_san'].search([], limit=1)

        # Tạo tài sản cho từng dòng chi tiết
        for line in self.line_ids:
            # ── Xử lý danh mục rỗng: dùng danh mục mặc định thay vì crash ──
            danh_muc = line.danh_muc_ts_id
            if not danh_muc:
                if not danh_muc_mac_dinh:
                    raise UserError(_(
                        'Dòng "%s" chưa có danh mục tài sản và hệ thống không tìm được danh mục nào.\n\n'
                        'Vui lòng tạo ít nhất 1 danh mục tài sản tại: Quản lý tài sản → Danh mục tài sản.'
                    ) % line.ten_thiet_bi)
                danh_muc = danh_muc_mac_dinh
            
            if line.so_luong <= 0:
                raise UserError(_('Dòng "%s" có số lượng không hợp lệ.\n\nSố lượng phải lớn hơn 0.') % line.ten_thiet_bi)
            
            # Tạo từng tài sản theo số lượng
            for i in range(int(line.so_luong)):
                # Chuẩn bị dữ liệu tài sản
                asset_vals = {
                    'ma_tai_san': 'New',
                    'ten_tai_san': line.ten_thiet_bi,
                    'ngay_mua_ts': self.ngay_phe_duyet or fields.Date.today(),
                    'don_vi_tien_te': self.don_vi_tien_te or 'vnd',
                    'gia_tri_ban_dau': line.don_gia or 1,
                    'gia_tri_hien_tai': line.don_gia or 1,
                    'danh_muc_ts_id': danh_muc.id,
                    'pp_khau_hao': line.pp_khau_hao or 'none',
                    'thoi_gian_su_dung': 0,
                    'thoi_gian_toi_da': line.thoi_gian_su_dung or 5,
                    'ty_le_khau_hao': line.ty_le_khau_hao or 20.0,
                    'don_vi_tinh': line.don_vi_tinh or 'Chiếc',
                    'ghi_chu': (
                        f'✅ Mua từ phê duyệt: {self.ma_phe_duyet}\n'
                        f'📋 Đề xuất gốc: {self.ma_de_xuat or "N/A"}\n'
                        f'📅 Ngày phê duyệt: {self.ngay_phe_duyet}\n'
                        f'👤 Người phê duyệt: {self.nguoi_phe_duyet_id.name if self.nguoi_phe_duyet_id else "N/A"}\n'
                        f'🏢 Phòng ban: {self.phong_ban_id.ten_phong_ban if self.phong_ban_id else "N/A"}\n'
                        f'📝 Mô tả: {line.mo_ta or "Không có"}'
                    ),
                }
                
                # Tạo tài sản
                try:
                    asset = tai_san_obj.create(asset_vals)
                    created_assets |= asset

                    # Mức 1: Phân bổ tài sản vào phòng ban từ HRM (đề xuất/phê duyệt)
                    if self.phong_ban_id:
                        self.env['phan_bo_tai_san'].create({
                            'tai_san_id': asset.id,
                            'phong_ban_id': self.phong_ban_id.id,
                            'vi_tri_tai_san_id': self.phong_ban_id.id,
                            'trang_thai': 'in-use',
                            'tinh_trang': 'binh_thuong',
                        })
                except Exception as e:
                    # Nếu lỗi khi tạo tài sản, báo rõ dòng nào bị lỗi
                    raise UserError(_(
                        'Lỗi khi tạo tài sản "%s" (số %s/%s):\n%s\n\n'
                        'Dữ liệu:\n- Mã: %s\n- Tên: %s\n- Danh mục: %s\n- Giá trị: %s %s'
                    ) % (
                        line.ten_thiet_bi, i+1, int(line.so_luong), str(e),
                        asset_code, line.ten_thiet_bi,
                        danh_muc.ten_danh_muc_ts if danh_muc else 'N/A',
                        line.don_gia, self.don_vi_tien_te or 'VND'
                    ))
        
        # Kiểm tra đã tạo tài sản thành công chưa
        if not created_assets:
            raise UserError(_('Không tạo được tài sản nào.\n\nVui lòng kiểm tra lại dữ liệu đơn phê duyệt.'))
        
        # Lưu liên kết tài sản vào đơn phê duyệt (quan trọng!)
        self.write({'tai_san_ids': [(6, 0, created_assets.ids)]})
        
        # Đồng bộ tài sản về đề xuất gốc (nếu có)
        if self.de_xuat_mua_id and self.de_xuat_mua_id.exists():
            try:
                # Kiểm tra xem đề xuất có trường tai_san_ids không
                if hasattr(self.de_xuat_mua_id, 'tai_san_ids'):
                    self.de_xuat_mua_id.write({'tai_san_ids': [(6, 0, created_assets.ids)]})
            except Exception as e:
                # Chỉ log warning, không block luồng chính
                self.message_post(
                    body=_('Cảnh báo: Không đồng bộ được tài sản về đề xuất gốc. Lỗi: %s') % str(e),
                    subject=_('Cảnh báo đồng bộ')
                )
        
        return created_assets
    
    def _create_journal_entry(self):
        """Tự động ghi nhận sổ cái — tự tạo tài khoản nếu chưa có"""
        self.ensure_one()

        if self.tong_gia_tri <= 0:
            raise UserError(_('Tổng giá trị phải lớn hơn 0 để tạo bút toán.'))

        # ---- Đảm bảo có Journal loại General ----
        journal = self.journal_id
        # Ưu tiên dùng journal type=general
        if not journal or journal.type != 'general':
            journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        if not journal:
            # Tạo journal general nếu chưa có
            journal = self.env['account.journal'].sudo().create({
                'name': 'Nhật ký chung',
                'code': 'MISC',
                'type': 'general',
            })
        if not journal:
            raise UserError(_('Không tìm thấy sổ nhật ký.'))

        # ---- Đảm bảo có TK Tài sản (211) ----
        tk_ts = self.tk_tai_san_id
        if not tk_ts:
            tk_ts = self.env['account.account'].search([
                ('deprecated', '=', False), ('code', '=like', '211%')
            ], limit=1)
        if not tk_ts:
            # Tự tạo TK 211
            user_type = (
                self.env.ref('account.data_account_type_fixed_assets', raise_if_not_found=False)
                or self.env['account.account.type'].search([('type', '=', 'other')], limit=1)
                or self.env['account.account.type'].search([], limit=1)
            )
            if not user_type:
                raise UserError(_('Không tìm thấy loại tài khoản. Vui lòng cài đặt sơ đồ tài khoản kế toán.'))
            tk_ts = self.env['account.account'].sudo().create({
                'code': '211',
                'name': 'Tài sản cố định hữu hình',
                'user_type_id': user_type.id,
                'reconcile': False,
            })

        # ---- Đảm bảo có TK Nguồn vốn (112) ----
        tk_nv = self.tk_nguon_von_id
        if not tk_nv:
            tk_nv = self.env['account.account'].search([
                ('deprecated', '=', False),
                '|', ('code', '=like', '112%'), ('code', '=like', '111%')
            ], limit=1)
        if not tk_nv:
            # Tự tạo TK 112
            user_type = (
                self.env.ref('account.data_account_type_liquidity', raise_if_not_found=False)
                or self.env['account.account.type'].search([('type', '=', 'liquidity')], limit=1)
                or self.env['account.account.type'].search([], limit=1)
            )
            if not user_type:
                raise UserError(_('Không tìm thấy loại tài khoản thanh khoản.'))
            tk_nv = self.env['account.account'].sudo().create({
                'code': '112',
                'name': 'Tiền gửi ngân hàng',
                'user_type_id': user_type.id,
                'reconcile': False,
            })

        # ---- Tạo bút toán ----
        try:
            move = self.env['account.move'].create({
                'journal_id': journal.id,
                'date': self.ngay_phe_duyet or fields.Date.today(),
                'ref': f'Mua tài sản - {self.ma_phe_duyet}',
                'line_ids': [
                    (0, 0, {
                        'name': f'Mua tài sản: {self.ten_de_xuat}',
                        'account_id': tk_ts.id,
                        'debit': self.tong_gia_tri,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': f'Thanh toán mua tài sản: {self.ten_de_xuat}',
                        'account_id': tk_nv.id,
                        'debit': 0.0,
                        'credit': self.tong_gia_tri,
                    }),
                ]
            })
        except Exception as e:
            # Nếu lỗi với journal hiện tại → thử với journal khác
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning("Lỗi tạo bút toán với journal %s: %s. Thử journal khác.", journal.name, e)
            # Tìm journal general
            journal_fallback = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
            if not journal_fallback:
                raise UserError(_('Không thể tạo bút toán: %s') % str(e))
            move = self.env['account.move'].create({
                'journal_id': journal_fallback.id,
                'date': self.ngay_phe_duyet or fields.Date.today(),
                'ref': f'Mua tài sản - {self.ma_phe_duyet}',
                'line_ids': [
                    (0, 0, {
                        'name': f'Mua tài sản: {self.ten_de_xuat}',
                        'account_id': tk_ts.id,
                        'debit': self.tong_gia_tri,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': f'Thanh toán mua tài sản: {self.ten_de_xuat}',
                        'account_id': tk_nv.id,
                        'debit': 0.0,
                        'credit': self.tong_gia_tri,
                    }),
                ]
            })
            journal = journal_fallback

        move.action_post()
        self.write({
            'but_toan_id': move.id,
            'tk_tai_san_id': tk_ts.id,
            'tk_nguon_von_id': tk_nv.id,
            'journal_id': journal.id,
        })

        # ── Tạo bút toán nội bộ (but_toan) để hiển thị trong menu Kế toán ──
        try:
            so_bt = self.env['ir.sequence'].next_by_code('but_toan.sequence') or f'BT-{self.ma_phe_duyet}'
            self.env['but_toan'].create({
                'so_but_toan': so_bt,
                'ngay_but_toan': self.ngay_phe_duyet or fields.Date.today(),
                'mo_ta': f'Mua tài sản – {self.ma_phe_duyet}: {self.ten_de_xuat or ""}',
                'tai_khoan_no_id': tk_ts.id,
                'tai_khoan_co_id': tk_nv.id,
                'so_tien': self.tong_gia_tri or 0,
                'trang_thai': 'posted',
                'khau_hao_id': self.khau_hao_ids[:1].id if self.khau_hao_ids else False,
            })
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f'Không tạo được but_toan nội bộ: {e}')

        return move
    
    def _create_depreciation_schedule(self):
        """Tạo lịch khấu hao tự động cho các tài sản"""
        self.ensure_one()
        
        khau_hao_obj = self.env['khau_hao_tai_san']
        
        for asset in self.tai_san_ids:
            if asset.pp_khau_hao == 'none':
                continue
            
            # Tạo bản ghi khấu hao với đầy đủ trường bắt buộc
            khau_hao_vals = {
                'tai_san_id': asset.id,
                'phe_duyet_mua_id': self.id,
                'ngay_bat_dau': self.ngay_phe_duyet or fields.Date.today(),
                'gia_tri_ban_dau': asset.gia_tri_ban_dau,
                'thoi_gian_khau_hao': asset.thoi_gian_toi_da or 0,
                'so_nam_khau_hao': asset.thoi_gian_toi_da or 5,  # Thêm trường bắt buộc
                'ty_le_khau_hao': asset.ty_le_khau_hao or 20.0,
                'phuong_phap': asset.pp_khau_hao or 'straight-line',
            }
            
            khau_hao_obj.create(khau_hao_vals)
    
    def _create_management_accounting(self):
        """Ghi nhận vào kế toán quản trị"""
        self.ensure_one()
        
        # Kiểm tra model có tồn tại không
        if 'tai_khoan_quan_tri' not in self.env:
            return
        
        tk_qt_obj = self.env['tai_khoan_quan_tri']
        
        # Tạo bản ghi kế toán quản trị với đầy đủ trường bắt buộc
        tk_qt_vals = {
            'ten_tai_khoan': f'Mua tài sản - {self.ma_phe_duyet}',
            'ma_tai_khoan': f'TK-{self.ma_phe_duyet}',  # Tạo mã tự động
            'phe_duyet_mua_id': self.id,
            'ngay_ghi_nhan': self.ngay_phe_duyet or fields.Date.today(),
            'loai_giao_dich': 'mua_tai_san',
            'mo_ta': f'Mua tài sản: {self.ten_de_xuat or ""}',
            'so_tien': self.tong_gia_tri or 0.0,
            'don_vi_tien_te': self.don_vi_tien_te or 'vnd',
            'phong_ban_id': self.phong_ban_id.id if self.phong_ban_id else False,
        }
        
        tk_qt_obj.create(tk_qt_vals)
    
    # ============ VIEW ACTIONS ============
    def action_view_assets(self):
        """Xem tài sản đã tạo"""
        self.ensure_one()
        return {
            'name': _('Tài sản đã tạo'),
            'type': 'ir.actions.act_window',
            'res_model': 'tai_san',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.tai_san_ids.ids)],
            'context': {'create': False}
        }
    
    def action_view_journal_entry(self):
        """Xem bút toán đã tạo"""
        self.ensure_one()
        if not self.but_toan_id:
            raise UserError(_('Chưa có bút toán nào được tạo.'))
        
        return {
            'name': _('Bút toán ghi nhận'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.but_toan_id.id if self.but_toan_id else False,
            'context': {'create': False}
        }
    
    def action_view_depreciation(self):
        """Xem lịch khấu hao"""
        self.ensure_one()
        return {
            'name': _('Lịch khấu hao tài sản'),
            'type': 'ir.actions.act_window',
            'res_model': 'khau_hao_tai_san',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.khau_hao_ids.ids)],
            'context': {'create': False}
        }
    
    def action_view_source_proposal(self):
        """Xem đề xuất gốc"""
        self.ensure_one()
        if not self.de_xuat_mua_id:
            raise UserError(_('Không tìm thấy đề xuất gốc.'))
        
        return {
            'name': _('Đề xuất mua tài sản'),
            'type': 'ir.actions.act_window',
            'res_model': 'de_xuat_mua_tai_san',
            'view_mode': 'form',
            'res_id': self.de_xuat_mua_id.id if self.de_xuat_mua_id else False,
            'target': 'current',
        }


class PheDuyetMuaTaiSanLine(models.Model):
    """Chi tiết phê duyệt mua tài sản"""
    _name = 'phe_duyet_mua_tai_san.line'
    _description = 'Chi tiết phê duyệt mua tài sản'
    _order = 'sequence, id'
    
    sequence = fields.Integer(string='STT', default=10)
    
    phe_duyet_id = fields.Many2one(
        'phe_duyet_mua_tai_san',
        string='Phê duyệt',
        required=True,
        ondelete='cascade'
    )
    
    # ============ THÔNG TIN THIẾT BỊ ============
    ten_thiet_bi = fields.Char(
        string='Tên thiết bị',
        required=True,
        readonly=True
    )
    
    danh_muc_ts_id = fields.Many2one(
        'danh_muc_tai_san',
        string='Danh mục tài sản',
        required=True,
        readonly=True,
        ondelete='restrict'
    )
    
    mo_ta = fields.Text(
        string='Mô tả',
        readonly=True
    )
    
    thong_so_ky_thuat = fields.Text(
        string='Thông số kỹ thuật',
        readonly=True
    )
    
    # ============ SỐ LƯỢNG VÀ GIÁ ============
    so_luong = fields.Integer(
        string='Số lượng',
        readonly=True
    )
    
    don_vi_tinh = fields.Char(
        string='Đơn vị tính',
        readonly=True
    )
    
    don_gia = fields.Float(
        string='Đơn giá',
        readonly=True
    )
    
    thanh_tien = fields.Float(
        string='Thành tiền',
        readonly=True
    )
    
    # ============ KHẤU HAO ============
    pp_khau_hao = fields.Selection([
        ('straight-line', 'Khấu hao tuyến tính'),
        ('degressive', 'Khấu hao giảm dần'),
        ('none', 'Không khấu hao')
    ], string='Phương pháp khấu hao', readonly=True)
    
    thoi_gian_su_dung = fields.Integer(
        string='Thời gian sử dụng (năm)',
        readonly=True
    )
    
    ty_le_khau_hao = fields.Float(
        string='Tỷ lệ khấu hao (%/năm)',
        readonly=True
    )
    
    # ============ NHÀ CUNG CẤP ============
    nha_cung_cap = fields.Char(
        string='Nhà cung cấp',
        readonly=True
    )

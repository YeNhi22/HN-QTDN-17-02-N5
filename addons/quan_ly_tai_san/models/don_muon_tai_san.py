# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

class DonMuonTaiSan(models.Model):
    _name = 'don_muon_tai_san'
    _description = 'Bảng chứa thông tin Đơn mượn tài sản'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "custom_rec_name"
    _order = "create_date desc"
    _sql_constraints = [
        ("ma_don_muon_unique", "unique(ma_don_muon)", "Mã đơn mượn đã tồn tại"),
    ]

    # ============ THÔNG TIN CƠ BẢN ============
    ma_don_muon = fields.Char(
        "Mã đơn mượn", 
        required=True, 
        default='New',
        readonly=True,
        copy=False,
        tracking=True
    )
    ten_don_muon = fields.Char('Tên đơn mượn', required=True, tracking=True)
    
    # ============ THÔNG TIN MƯỢN ============
    phong_ban_cho_muon_id = fields.Many2one(
        'phong_ban', 
        string='Phòng ban cho mượn', 
        required=True, 
        ondelete='restrict',
        tracking=True
    )
    thoi_gian_muon = fields.Datetime(
        'Thời gian mượn', 
        required=True, 
        default=lambda self: fields.Datetime.now(),
        tracking=True
    )
    thoi_gian_tra = fields.Datetime(
        'Thời gian trả dự kiến', 
        required=True,
        tracking=True
    )
    nhan_vien_muon_id = fields.Many2one(
        'nhan_vien', 
        string='Nhân viên mượn', 
        required=True, 
        ondelete='restrict',
        tracking=True
    )
    phong_ban_loc_nv_id = fields.Many2one(
        'phong_ban',
        string='Lọc NV theo phòng ban',
        help='Chọn phòng ban để thu hẹp danh sách nhân viên mượn (để trống = tất cả NV).',
        ondelete='set null',
    )
    
    ly_do = fields.Text('Lý do mượn', required=True)
    ghi_chu = fields.Text('Ghi chú')
    
    # ============ LIÊN KẾT PHIẾU MƯỢN TRẢ (Mức 2 - tự động hóa) ============
    muon_tra_ids = fields.One2many(
        'muon_tra_tai_san',
        'ma_don_muon_id',
        string='Phiếu mượn trả',
        readonly=True,
    )

    # ============ DANH SÁCH TÀI SẢN ============
    phan_bo_chon_ids = fields.Many2many(
        'phan_bo_tai_san',
        'don_muon_phan_bo_rel',
        'don_muon_id',
        'phan_bo_id',
        string='Tài sản mượn',
        help='Chọn tài sản thuộc phòng ban cho mượn. Có thể chọn trước khi Lưu lần đầu.',
    )
    don_muon_tai_san_ids = fields.One2many(
        'don_muon_tai_san_line', 
        'don_muon_id', 
        string='Danh sách tài sản mượn'
    )
    ds_tai_san_chua_muon = fields.Many2many(
        'phan_bo_tai_san', 
        compute='_compute_ds_tai_san_chua_muon', 
        string="Tài sản có thể mượn"
    )
    
    # ============ TRẠNG THÁI ============
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('dang_muon', 'Đang mượn'),
        ('da_tra', 'Đã trả'),
        ('tu_choi', 'Từ chối'),
        ('huy', 'Đã hủy')
    ], string='Trạng thái', required=True, default='nhap', tracking=True)
    
    # ============ THÔNG TIN DUYỆT ============
    nguoi_duyet_id = fields.Many2one(
        'res.users',
        string='Người duyệt',
        readonly=True,
        tracking=True
    )
    ngay_duyet = fields.Datetime('Ngày duyệt', readonly=True)
    ly_do_tu_choi = fields.Text('Lý do từ chối')
    
    # ============ THÔNG TIN TRẢ ============
    ngay_tra_thuc_te = fields.Datetime('Ngày trả thực tế', readonly=True)
    nguoi_xac_nhan_tra_id = fields.Many2one(
        'res.users',
        string='Người xác nhận trả',
        readonly=True
    )
    
    # ============ COMPUTED FIELDS ============
    custom_rec_name = fields.Char(
        compute='_compute_custom_rec_name', 
        string='Tên hiển thị',
        store=True
    )
    
    so_tai_san = fields.Integer(
        compute='_compute_so_tai_san',
        string='Số tài sản mượn'
    )
    
    tinh_trang = fields.Char(
        compute='_compute_tinh_trang',
        string='Tình trạng'
    )
    
    # ============ COMPUTE METHODS ============
    @api.depends('ma_don_muon', 'ten_don_muon')
    def _compute_custom_rec_name(self):
        for record in self:
            if record.ma_don_muon and record.ten_don_muon:
                record.custom_rec_name = f"{record.ma_don_muon} - {record.ten_don_muon}"
            else:
                record.custom_rec_name = record.ma_don_muon or 'New'
    
    @api.depends('don_muon_tai_san_ids', 'phan_bo_chon_ids')
    def _compute_so_tai_san(self):
        for record in self:
            if record.don_muon_tai_san_ids:
                record.so_tai_san = len(record.don_muon_tai_san_ids)
            else:
                record.so_tai_san = len(record.phan_bo_chon_ids)

    @api.depends(
        'phong_ban_cho_muon_id',
        'don_muon_tai_san_ids', 'don_muon_tai_san_ids.phan_bo_tai_san_id',
        'phan_bo_chon_ids',
    )
    def _compute_ds_tai_san_chua_muon(self):
        for record in self:
            selected_ids = (
                record.don_muon_tai_san_ids.mapped('phan_bo_tai_san_id')
                | record.phan_bo_chon_ids
            ).ids
            pb_id = record.phong_ban_cho_muon_id.id if record.phong_ban_cho_muon_id else False
            # Chỉ loại TS đang mượn/hỏng/mất; NV "sử dụng" trên phân bổ ≠ đang mượn tạm
            available = self.env['phan_bo_tai_san'].search([
                ('phong_ban_id', '=', pb_id),
                ('trang_thai', '=', 'in-use'),
                ('tinh_trang', 'in', ['binh_thuong']),
            ])
            # Giữ TS đã chọn trong danh sách để domain không xóa dòng sau khi Lưu
            if selected_ids:
                selected = self.env['phan_bo_tai_san'].browse(selected_ids)
                record.ds_tai_san_chua_muon = available | selected
            else:
                record.ds_tai_san_chua_muon = available

    @api.onchange('phong_ban_cho_muon_id')
    def _onchange_phong_ban_cho_muon_id(self):
        """Đổi phòng ban cho mượn → xóa TS không thuộc phòng mới (NV mượn giữ nguyên — có thể khác phòng)."""
        if self.phong_ban_cho_muon_id and self.phan_bo_chon_ids:
            invalid_pb = self.phan_bo_chon_ids.filtered(
                lambda p: p.phong_ban_id != self.phong_ban_cho_muon_id
            )
            if invalid_pb:
                self.phan_bo_chon_ids = self.phan_bo_chon_ids - invalid_pb
        if self.phong_ban_cho_muon_id and self.don_muon_tai_san_ids:
            invalid = self.don_muon_tai_san_ids.filtered(
                lambda l: l.phan_bo_tai_san_id
                and l.phan_bo_tai_san_id.phong_ban_id != self.phong_ban_cho_muon_id
            )
            if invalid:
                self.don_muon_tai_san_ids = self.don_muon_tai_san_ids - invalid

    @api.onchange('phong_ban_loc_nv_id')
    def _onchange_phong_ban_loc_nv_id(self):
        """Đổi bộ lọc NV → xóa NV không thuộc phòng đã lọc."""
        if self.phong_ban_loc_nv_id and self.nhan_vien_muon_id \
                and self.nhan_vien_muon_id.phong_ban_hien_tai_id != self.phong_ban_loc_nv_id:
            self.nhan_vien_muon_id = False

    @api.constrains('phan_bo_chon_ids', 'phong_ban_cho_muon_id', 'trang_thai')
    def _constrains_phan_bo_chon(self):
        for record in self:
            if record.trang_thai != 'nhap' or not record.phong_ban_cho_muon_id:
                continue
            invalid = record.phan_bo_chon_ids.filtered(
                lambda p: p.phong_ban_id != record.phong_ban_cho_muon_id
            )
            if invalid:
                names = ', '.join(invalid.mapped('tai_san_id.ma_tai_san'))
                raise ValidationError(_(
                    'Tài sản %s không thuộc phòng ban cho mượn.'
                ) % names)

    @api.depends('trang_thai', 'thoi_gian_muon', 'thoi_gian_tra')
    def _compute_tinh_trang(self):
        for record in self:
            if record.trang_thai == 'da_tra':
                record.tinh_trang = '✅ Đã hoàn trả'
            elif record.trang_thai == 'dang_muon':
                now = fields.Datetime.now()
                if record.thoi_gian_tra and now > record.thoi_gian_tra:
                    record.tinh_trang = '⚠️ Quá hạn trả'
                else:
                    record.tinh_trang = '📦 Đang mượn'
            elif record.trang_thai == 'da_duyet':
                record.tinh_trang = '✔️ Đã duyệt - Chờ nhận'
            elif record.trang_thai == 'cho_duyet':
                record.tinh_trang = '⏳ Đang chờ duyệt'
            elif record.trang_thai == 'tu_choi':
                record.tinh_trang = '❌ Đã từ chối'
            elif record.trang_thai == 'huy':
                record.tinh_trang = '🚫 Đã hủy'
            else:
                record.tinh_trang = '📝 Nháp'
    
    # ============ CONSTRAINTS ============
    @api.constrains('thoi_gian_muon', 'thoi_gian_tra')
    def _constrains_thoi_gian(self):
        for record in self:
            if record.thoi_gian_muon and record.thoi_gian_tra:
                if record.thoi_gian_muon > record.thoi_gian_tra:
                    raise ValidationError("Thời gian mượn phải trước thời gian trả dự kiến!")
    
    @api.constrains('don_muon_tai_san_ids', 'phan_bo_chon_ids', 'trang_thai')
    def _constrains_don_muon_tai_san_ids(self):
        for record in self:
            if record.trang_thai not in ['nhap', 'cho_duyet']:
                if not record.don_muon_tai_san_ids:
                    raise ValidationError("Đơn mượn phải có ít nhất một tài sản!")
    
    def _sync_lines_from_phan_bo_chon(self):
        """Đồng bộ chi tiết dòng từ danh sách tài sản đã chọn."""
        Line = self.env['don_muon_tai_san_line']
        for record in self:
            if record.trang_thai != 'nhap':
                continue
            target = record.phan_bo_chon_ids
            existing = record.don_muon_tai_san_ids
            (existing.filtered(
                lambda l: l.phan_bo_tai_san_id not in target
            )).unlink()
            current_pb = record.don_muon_tai_san_ids.mapped('phan_bo_tai_san_id')
            for pb in target - current_pb:
                Line.create({
                    'don_muon_id': record.id,
                    'phan_bo_tai_san_id': pb.id,
                })

    # ============ CRUD METHODS ============
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'ma_don_muon' in fields_list:
            res['ma_don_muon'] = self.env['sequence.helper'].get_default_code(
                'don_muon_tai_san', 'ma_don_muon', 'don_muon_tai_san', 'DMT'
            )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        self.env['sequence.helper'].assign_codes_multi(
            vals_list, 'ma_don_muon', 'don_muon_tai_san', 'DMT', 'don_muon_tai_san'
        )
        records = super(DonMuonTaiSan, self).create(vals_list)
        for record in records:
            record._sync_lines_from_phan_bo_chon()
        return records

    def write(self, vals):
        res = super(DonMuonTaiSan, self).write(vals)
        if 'phan_bo_chon_ids' in vals or 'phong_ban_cho_muon_id' in vals:
            self.filtered(lambda r: r.trang_thai == 'nhap')._sync_lines_from_phan_bo_chon()
        return res

    def unlink(self):
        blocked = {
            'cho_duyet': _('Chờ duyệt'),
            'da_duyet': _('Đã duyệt'),
            'dang_muon': _('Đang mượn'),
            'da_tra': _('Đã trả'),
        }
        for record in self:
            if record.trang_thai in blocked:
                raise UserError(_(
                    'Không thể xóa đơn ở trạng thái "%s".\n'
                    'Hãy hủy đơn hoặc hoàn tất trả tài sản trước.'
                ) % blocked[record.trang_thai])
            record._cancel_linked_muon_tra(_('Đơn bị xóa'))
        return super(DonMuonTaiSan, self).unlink()

    def _get_active_muon_tra(self):
        """Phiếu mượn trả đang xử lý (chưa kết thúc)."""
        self.ensure_one()
        # Đơn đã hủy/từ chối/hoàn tất → không còn phiếu đang chặn thao tác
        if self.trang_thai in ('huy', 'tu_choi', 'da_tra'):
            return self.env['muon_tra_tai_san']
        return self.env['muon_tra_tai_san'].search([
            ('ma_don_muon_id', '=', self.id),
            ('trang_thai', 'not in', ['tu_choi', 'da_tra']),
        ], limit=1, order='create_date desc')

    def _map_don_muon_lines_by_phan_bo(self):
        """Map phan_bo_tai_san_id -> don_muon_tai_san_line."""
        self.ensure_one()
        return {
            line.phan_bo_tai_san_id.id: line
            for line in self.don_muon_tai_san_ids
            if line.phan_bo_tai_san_id
        }

    def sync_from_muon_tra_approved(self, muon_tra):
        """Đồng bộ trạng thái đã duyệt từ phiếu mượn trả."""
        self.ensure_one()
        self.write({
            'trang_thai': 'da_duyet',
            'nguoi_duyet_id': muon_tra.nguoi_duyet_id.id,
            'ngay_duyet': muon_tra.ngay_duyet,
        })
        # ── Nhóm 5: Gửi email thông báo phê duyệt ────────────
        try:
            self.env['email.notification.service'].notify_don_muon_duyet(self)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f'Email notify approved failed: {e}')

    def sync_from_muon_tra_rejected(self, muon_tra):
        """Đồng bộ trạng thái từ chối từ phiếu mượn trả."""
        self.ensure_one()
        self.write({
            'trang_thai': 'tu_choi',
            'nguoi_duyet_id': muon_tra.nguoi_duyet_id.id,
            'ngay_duyet': muon_tra.ngay_duyet,
            'ly_do_tu_choi': muon_tra.ly_do_tu_choi,
        })
        # ── Nhóm 5: Gửi email thông báo từ chối ──────────────
        try:
            self.env['email.notification.service'].notify_don_muon_tu_choi(
                self, muon_tra.ly_do_tu_choi or '')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f'Email notify rejected failed: {e}')

    def sync_from_muon_tra_borrowed(self, muon_tra):
        """Đồng bộ trạng thái đang mượn từ phiếu mượn trả."""
        self.ensure_one()
        now = muon_tra.thoi_gian_muon_thuc_te or fields.Datetime.now()
        line_map = self._map_don_muon_lines_by_phan_bo()
        for mt_line in muon_tra.muon_tra_line_ids:
            dm_line = line_map.get(mt_line.phan_bo_tai_san_id.id)
            if dm_line:
                dm_line.write({
                    'thoi_gian_cho_muon': now,
                    'nguoi_giao_id': muon_tra.nguoi_giao_id.id,
                    'trang_thai_line': 'dang_muon',
                    'tinh_trang_truoc_muon': 'binh_thuong',
                })
        self.write({
            'trang_thai': 'dang_muon',
            'thoi_gian_muon': now,
        })

    def sync_from_muon_tra_returned(self, muon_tra):
        """Đồng bộ trạng thái đã trả từ phiếu mượn trả."""
        self.ensure_one()
        now = muon_tra.thoi_gian_tra_thuc_te or fields.Datetime.now()
        line_map = self._map_don_muon_lines_by_phan_bo()
        for mt_line in muon_tra.muon_tra_line_ids:
            dm_line = line_map.get(mt_line.phan_bo_tai_san_id.id)
            if not dm_line:
                continue
            trang_thai_line = 'da_tra'
            if mt_line.tinh_trang_khi_tra == 'hu_hong':
                trang_thai_line = 'hong'
            elif mt_line.tinh_trang_khi_tra == 'mat':
                trang_thai_line = 'mat'
            dm_line.write({
                'tinh_trang_sau_tra': mt_line.tinh_trang_khi_tra,
                'thoi_gian_tra_thuc_te': now,
                'nguoi_nhan_tra_id': muon_tra.nguoi_nhan_tra_id.id,
                'trang_thai_line': trang_thai_line,
                'ghi_chu_tinh_trang': mt_line.ghi_chu_tra or '',
            })
        self.write({
            'trang_thai': 'da_tra',
            'ngay_tra_thuc_te': now,
            'nguoi_xac_nhan_tra_id': muon_tra.nguoi_nhan_tra_id.id,
        })

    def _get_don_muon_lines_for_submit(self):
        """Lấy dòng tài sản hợp lệ sau khi đồng bộ từ Many2many."""
        self.ensure_one()
        self._sync_lines_from_phan_bo_chon()
        self.flush()
        return self.env['don_muon_tai_san_line'].search([
            ('don_muon_id', '=', self.id),
            ('phan_bo_tai_san_id', '!=', False),
        ])

    def _cancel_linked_muon_tra(self, ly_do):
        """Hủy mọi phiếu mượn trả chưa kết thúc khi đơn bị hủy/reset."""
        self.ensure_one()
        linked = self.env['muon_tra_tai_san'].search([
            ('ma_don_muon_id', '=', self.id),
            ('trang_thai', 'not in', ['tu_choi', 'da_tra']),
        ])
        for phieu in linked:
            phieu._release_phan_bo_assets()
            phieu.write({
                'trang_thai': 'tu_choi',
                'ly_do_tu_choi': ly_do,
                'nguoi_duyet_id': self.env.user.id,
                'ngay_duyet': fields.Datetime.now(),
            })
    
    # ============ ACTION METHODS ============
    def action_gui_duyet(self):
        """Gửi đơn để duyệt - Tự động tạo phiếu trong Quản lý mượn trả"""
        for record in self:
            if isinstance(record.id, models.NewId):
                raise UserError(_('Vui lòng lưu đơn mượn trước khi gửi duyệt!'))

            if record.trang_thai != 'nhap':
                raise UserError(_('Chỉ có thể gửi duyệt đơn ở trạng thái Nháp!'))

            # Đồng bộ từ danh sách tài sản đã chọn (Many2many — hoạt động cả trước Lưu lần đầu)
            record._sync_lines_from_phan_bo_chon()

            if not record.phan_bo_chon_ids:
                raise UserError(_(
                    'Đơn mượn phải có ít nhất một tài sản!\n\n'
                    'Quy trình: (1) Chọn Phòng ban cho mượn → (2) Chọn tài sản mượn → '
                    '(3) Lưu → (4) Gửi duyệt.'
                ))

            invalid = record.phan_bo_chon_ids.filtered(
                lambda p: p.phong_ban_id != record.phong_ban_cho_muon_id
            )
            if invalid:
                names = ', '.join(
                    (p.tai_san_id.ma_tai_san or p.display_name) for p in invalid
                )
                raise UserError(_(
                    'Tài sản %s không thuộc phòng ban cho mượn "%s".\n'
                    'Chỉ chọn tài sản đang phân bổ cho phòng ban đó.'
                ) % (names, record.phong_ban_cho_muon_id.ten_phong_ban))

            lines = record._get_don_muon_lines_for_submit()
            if not lines:
                raise UserError(_(
                    'Không tạo được dòng tài sản. Vui lòng Lưu đơn sau khi chọn tài sản rồi thử lại.'
                ))

            # Dọn phiếu sót (đơn nháp nhưng còn phiếu cũ chưa đóng)
            stale = self.env['muon_tra_tai_san'].search([
                ('ma_don_muon_id', '=', record.id),
                ('trang_thai', 'not in', ['tu_choi', 'da_tra']),
            ])
            if stale:
                record._cancel_linked_muon_tra(
                    _('Hủy phiếu sót trước khi gửi duyệt lại')
                )

            existing = record._get_active_muon_tra()
            if existing:
                raise UserError(_(
                    'Đơn mượn đã có phiếu mượn trả đang xử lý: %s'
                ) % existing.ma_phieu_muon_tra)

            record.write({'trang_thai': 'cho_duyet'})

            muon_tra_lines = []
            for line in lines:
                muon_tra_lines.append((0, 0, {
                    'phan_bo_tai_san_id': line.phan_bo_tai_san_id.id,
                    'ghi_chu': line.ghi_chu or '',
                }))

            muon_tra = self.env['muon_tra_tai_san'].create({
                'ma_don_muon_id': record.id,
                'ten_phieu_muon_tra': _('Duyệt đơn mượn %s') % record.ma_don_muon,
                'phong_ban_cho_muon_id': record.phong_ban_cho_muon_id.id,
                'nhan_vien_muon_id': record.nhan_vien_muon_id.id,
                'thoi_gian_muon': record.thoi_gian_muon,
                'thoi_gian_tra_du_kien': record.thoi_gian_tra,
                'ly_do_muon': record.ly_do or '',
                'trang_thai': 'cho_duyet',
                'muon_tra_line_ids': muon_tra_lines,
            })

            record.message_post(
                body=_('📤 Đơn mượn đã gửi phê duyệt. Mã phiếu: %s') % muon_tra.ma_phieu_muon_tra
            )

            # ── Nhóm 5: Gửi email xác nhận cho nhân viên ────────
            try:
                self.env['email.notification.service'].notify_don_muon_gui_duyet(record)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f'Email notify failed: {e}')

            self.env['system.event'].safe_emit(
                'don_muon.submitted',
                f'Đơn mượn {record.ma_don_muon} đã gửi',
                source_model='don_muon_tai_san',
                source_id=record.id,
                payload={
                    'ma_don_muon': record.ma_don_muon,
                    'nhan_vien': record.nhan_vien_muon_id.ho_ten if record.nhan_vien_muon_id else '—',
                    'ma_phieu': muon_tra.ma_phieu_muon_tra,
                    'so_tai_san': record.so_tai_san,
                },
            )
    
    def action_huy(self):
        """Hủy đơn mượn"""
        for record in self:
            if record.trang_thai in ['dang_muon', 'da_tra']:
                raise UserError(_('Không thể hủy đơn đang mượn hoặc đã trả!'))
            record._cancel_linked_muon_tra(_('Đơn mượn đã bị hủy'))
            record.write({'trang_thai': 'huy'})
            record.message_post(body=_('🚫 Đơn mượn đã bị hủy.'))
    
    def action_dat_lai_nhap(self):
        """Đặt lại về trạng thái nháp"""
        for record in self:
            if record.trang_thai not in ['tu_choi', 'huy']:
                raise UserError(_('Chỉ có thể đặt lại đơn bị từ chối hoặc đã hủy!'))
            record._cancel_linked_muon_tra(_('Đơn được đặt lại nháp'))
            record.write({
                'trang_thai': 'nhap',
                'nguoi_duyet_id': False,
                'ngay_duyet': False,
                'ly_do_tu_choi': False,
            })
            record.message_post(body=_('📝 Đơn mượn đã được đặt lại về trạng thái Nháp.'))
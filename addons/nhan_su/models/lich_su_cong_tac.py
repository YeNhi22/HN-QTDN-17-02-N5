from odoo import models, fields, api


class LichSuCongTac(models.Model):
    _name = 'lich_su_cong_tac'
    _description = 'Bảng chứa thông tin lịch sử công tác'

    time_start = fields.Date("Thời gian bắt đầu", required=True, default=lambda self: fields.Date.today())
    time_end = fields.Date("Thời gian kết thúc", required=True, default=lambda self: fields.Date.today())
    phong_ban_id = fields.Many2one("phong_ban", string="Phòng ban", required=True)
    chuc_vu_id = fields.Many2one("chuc_vu", string="Chức vụ", required=True)
    nhan_vien_id = fields.Many2one("nhan_vien", string="Nhân viên", required=True)

    @api.model
    def create(self, vals):
        records = super().create(vals)
        records._trigger_hrm_sync()
        return records

    def write(self, vals):
        # Lưu phòng ban/chức vụ HRM *trước* khi ghi — so sánh computed field nhân viên
        old_employee_state = {}
        for rec in self:
            if rec.nhan_vien_id:
                nv = rec.nhan_vien_id
                old_employee_state[nv.id] = (
                    nv.phong_ban_hien_tai_id,
                    nv.chuc_vu_hien_tai_id,
                )

        res = super().write(vals)

        affected_nv_ids = set()
        for rec in self:
            if rec.nhan_vien_id:
                affected_nv_ids.add(rec.nhan_vien_id.id)

        for nv_id in affected_nv_ids:
            nv = self.env['nhan_vien'].browse(nv_id)
            old_pb, old_cv = old_employee_state.get(nv_id, (False, False))
            new_pb = nv.phong_ban_hien_tai_id
            new_cv = nv.chuc_vu_hien_tai_id
            if old_pb != new_pb or old_cv != new_cv:
                self.env['hrm.sync.log'].log_department_change(
                    nv, old_pb, new_pb, old_cv, new_cv
                )
                self.env['system.event'].safe_emit(
                        'hrm.department_changed',
                        f'HRM: {nv.ho_ten} chuyển phòng ban',
                        source_model='nhan_vien',
                        source_id=nv.id,
                        payload={
                            'nhan_vien': nv.ho_ten,
                            'phong_ban_cu': old_pb.ten_phong_ban if old_pb else '—',
                            'phong_ban_moi': new_pb.ten_phong_ban if new_pb else '—',
                        },
                    )
        return res

    def _trigger_hrm_sync(self):
        for rec in self:
            if rec.nhan_vien_id:
                pb = rec.nhan_vien_id.phong_ban_hien_tai_id
                cv = rec.nhan_vien_id.chuc_vu_hien_tai_id
                self.env['hrm.sync.log'].log_department_change(
                    rec.nhan_vien_id, False, pb, False, cv
                )

# -*- coding: utf-8 -*-
import re

from odoo import models, api
from odoo.exceptions import ValidationError


class SequenceHelper(models.AbstractModel):
    """Helper sinh mã tự động dạng PREFIX001 (NV, PB, CV...)."""
    _name = 'sequence.helper'
    _description = 'Sequence Helper'

    @api.model
    def next_code(self, sequence_code, fallback='New'):
        return self.env['ir.sequence'].next_by_code(sequence_code) or fallback

    @api.model
    def sync_sequence_before_generation(self, sequence_code, prefix, model_name, field_name):
        """Đồng bộ sequence number_next về max_existing_num + 1 trước khi sinh mã."""
        try:
            seq = self.env['ir.sequence'].sudo().search([('code', '=', sequence_code)], limit=1)
            if not seq:
                return
            
            # Lấy tất cả mã hiện có bắt đầu bằng prefix
            records = self.env[model_name].sudo().search_read(
                [(field_name, '=like', f'{prefix}%')], [field_name]
            )
            max_num = 0
            for rec in records:
                val = rec.get(field_name)
                if val:
                    # Tách phần số từ mã (ví dụ: NV007 -> 7)
                    match = re.match(rf'^{re.escape(prefix)}(\d+)$', str(val).strip(), re.IGNORECASE)
                    if match:
                        num = int(match.group(1))
                        if num > max_num:
                            max_num = num
            
            # Cập nhật number_next của sequence về max_num + 1
            seq.write({'number_next': max_num + 1})
        except Exception:
            pass

    @api.model
    def get_default_code(self, model_name, field_name, sequence_code, prefix):
        """Đồng bộ sequence theo dữ liệu thực tế và sinh mã mặc định cho form view."""
        self.sync_sequence_before_generation(sequence_code, prefix, model_name, field_name)
        return self.next_code(sequence_code, 'New')

    @api.model
    def sync_sequence_from_code(self, code, sequence_code, prefix):
        """Sau import / nhập tay mã lớn hơn sequence hiện tại → tăng number_next."""
        if not code or not prefix:
            return
        match = re.match(rf'^{re.escape(prefix)}(\d+)$', str(code).strip(), re.IGNORECASE)
        if not match:
            return
        num = int(match.group(1))
        seq = self.env['ir.sequence'].sudo().search([('code', '=', sequence_code)], limit=1)
        if seq and seq.number_next <= num:
            seq.write({'number_next': num + 1})

    @api.model
    def assign_code(self, vals, field_name, sequence_code, prefix):
        """Gán mã tự động nếu trống; đồng bộ sequence nếu người dùng/import nhập sẵn."""
        code = (vals.get(field_name) or '').strip()
        if not code or code == 'New':
            vals[field_name] = self.next_code(sequence_code, 'New')
        else:
            vals[field_name] = code.upper() if prefix.isalpha() else code
            self.sync_sequence_from_code(vals[field_name], sequence_code, prefix)
        return vals[field_name]

    @api.model
    def assign_codes_multi(self, vals_list, field_name, sequence_code, prefix, model_name):
        """Tự động sinh và gán mã duy nhất cho một danh sách bản ghi, xử lý trùng lặp trong lô và cơ sở dữ liệu (hỗ trợ import)."""
        self.sync_sequence_before_generation(sequence_code, prefix, model_name, field_name)
        assigned_in_batch = set()
        for vals in vals_list:
            code = str(vals.get(field_name) or '').strip()
            is_empty = not code or code == 'New' or code.lower() in ('false', 'none', 'null')
            
            is_duplicate = False
            if not is_empty:
                # Check duplicate in current batch or database
                if code in assigned_in_batch or self.env[model_name].sudo().search_count([(field_name, '=', code)]) > 0:
                    is_duplicate = True
            
            if is_empty or is_duplicate:
                # Sinh mã mới cho đến khi không còn trùng
                new_code = self.next_code(sequence_code, 'New')
                while new_code in assigned_in_batch or self.env[model_name].sudo().search_count([(field_name, '=', new_code)]) > 0:
                    new_code = self.next_code(sequence_code, 'New')
                vals[field_name] = new_code
            else:
                vals[field_name] = code.upper() if prefix.isalpha() else code
                self.sync_sequence_from_code(vals[field_name], sequence_code, prefix)
                
            assigned_in_batch.add(vals[field_name])

    @api.model
    def check_duplicate_code(self, model, field_name, code, exclude_ids=None):
        if not code or code == 'New':
            return
        domain = [(field_name, '=', code)]
        if exclude_ids:
            domain.append(('id', 'not in', list(exclude_ids)))
        if self.env[model].sudo().search_count(domain):
            raise ValidationError(f'Mã "{code}" đã tồn tại, không được trùng.')

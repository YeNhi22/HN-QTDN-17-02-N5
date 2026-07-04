# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class HideUnrelatedMenus(models.AbstractModel):
    """
    Ẩn các menu không liên quan đến đề tài khi cài module.
    Dùng AbstractModel để không tạo bảng trong DB.
    Chạy sau khi module được cài/update.
    """
    _name = 'q_trang_chu.hide_menus'
    _description = 'Ẩn menu không liên quan'

    # Danh sách xmlid các menu cần ẩn
    MENUS_TO_HIDE = [
        'mail.menu_root_discuss',   # Thảo luận
        'account.menu_finance',     # Lên hóa đơn
        'hr.menu_hr_root',          # Nhân viên (hr built-in)
    ]

    # Danh sách xmlid các menu cần đảm bảo hiện
    MENUS_TO_SHOW = [
        'base.menu_management',     # Ứng dụng
    ]

    @api.model
    def _hide_unrelated_menus(self):
        """Ẩn menu không liên quan, bỏ qua nếu module chưa cài"""
        for xmlid in self.MENUS_TO_HIDE:
            try:
                menu = self.env.ref(xmlid, raise_if_not_found=False)
                if menu and menu.active:
                    menu.sudo().write({'active': False})
                    _logger.info('Đã ẩn menu: %s', xmlid)
            except Exception as e:
                _logger.warning('Không thể ẩn menu %s: %s', xmlid, e)

        for xmlid in self.MENUS_TO_SHOW:
            try:
                menu = self.env.ref(xmlid, raise_if_not_found=False)
                if menu and not menu.active:
                    menu.sudo().write({'active': True})
                    _logger.info('Đã hiện menu: %s', xmlid)
            except Exception as e:
                _logger.warning('Không thể hiện menu %s: %s', xmlid, e)

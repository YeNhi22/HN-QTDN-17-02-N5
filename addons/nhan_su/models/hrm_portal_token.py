# -*- coding: utf-8 -*-
import secrets
from datetime import timedelta

from odoo import models, fields, api


class HrmPortalToken(models.Model):
    """Token đăng nhập cổng web — tách biệt session Odoo backend."""
    _name = 'hrm.portal.token'
    _description = 'HRM Portal Token'
    _order = 'create_date desc'

    token = fields.Char(required=True, index=True, copy=False)
    nhan_vien_id = fields.Many2one('nhan_vien', required=True, ondelete='cascade')
    expire_at = fields.Datetime(required=True, index=True)
    active = fields.Boolean(default=True)

    @api.model
    def create_token(self, employee, hours=12):
        self.search([
            ('nhan_vien_id', '=', employee.id),
            ('active', '=', True),
        ]).write({'active': False})
        token = secrets.token_urlsafe(32)
        record = self.sudo().create({
            'token': token,
            'nhan_vien_id': employee.id,
            'expire_at': fields.Datetime.now() + timedelta(hours=hours),
        })
        return record.token

    @api.model
    def resolve(self, token):
        if not token:
            return self.env['nhan_vien']
        row = self.sudo().search([
            ('token', '=', token),
            ('active', '=', True),
            ('expire_at', '>', fields.Datetime.now()),
        ], limit=1)
        return row.nhan_vien_id if row else self.env['nhan_vien']

    @api.model
    def revoke(self, token):
        if token:
            self.sudo().search([('token', '=', token)]).write({'active': False})

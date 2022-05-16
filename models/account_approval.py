# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    approved_by = fields.Many2one('res.users', string='Approved by')


class DiscountSettings(models.Model):
    _name = 'discount.settings'
    _description = 'Discount Settings'

    name = fields.Char()
    max_amount = fields.Integer(required=True)
    group_ids = fields.Many2many("res.groups", string="Allowed Groups")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.constrains('discount')
    def _check_max_allowed_discount(self):
        max_discount_allowed = self.env['discount.settings'].search_read([
            ('group_ids', 'in', self.env.user.groups_id.ids)
        ], ['max_amount'], order='max_amount DESC', limit=1)
        fallback_value = 999 if self.env.is_admin() else 0
        max_discount = max_discount_allowed and max_discount_allowed[0]['max_amount'] or fallback_value

        for line in self:
            if line.discount > max_discount:
                raise ValidationError("Vous ne pouvez pas appliquer une réduction supérieure à ce que votre niveau permet (%s%%). Demandez à votre manager pour accorder une réduction supérieure." % max_discount)

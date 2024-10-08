# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

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

    can_edit_price_unit = fields.Boolean(compute='_compute_can_edit_price_unit')

    @api.depends_context('uid')
    @api.depends('product_type')
    def _compute_can_edit_price_unit(self):
        if self.env.user.has_group('account_approval.group_so_price_modification'):
            self.can_edit_price_unit = True
        else:
            service_lines = self.filtered(lambda line: line.product_type == 'service')
            service_lines.can_edit_price_unit = True
            (self - service_lines).can_edit_price_unit = False

    @api.constrains('discount')
    def _check_max_allowed_discount(self):
        for line in self:
            pricelist_item_name = line.pricelist_item_id.name if line.pricelist_item_id else 'None'
            _logger.info('Checking discount for line: %s, Pricelist Item ID: %s, Pricelist Item Name: %s', line.id, line.pricelist_item_id.id if line.pricelist_item_id else 'None', pricelist_item_name)
                
            if self.env.is_admin():
                continue  # Si admin, on saute toutes les vérifications

            if not self._context.get('bypass_max_discount_check'):
                if line.pricelist_item_id:
                    pricelist_item = line.pricelist_item_id
                    compute_price = pricelist_item.compute_price
                    _logger.info('Line %s: Pricelist compute_price type is %s.', line.id, compute_price)

                    if compute_price == 'fixed':
                        discounted_price = line.price_unit * (1 - abs(line.discount) / 100.0)
                        _logger.info('Line %s: Calculated discounted price is %s.', line.id, discounted_price)
                        if discounted_price < pricelist_item.fixed_price:
                            _logger.warning('Line %s: Discounted price %s is less than fixed pricelist price %s.', line.id, discounted_price, pricelist_item.fixed_price)
                            raise ValidationError("Vous ne pouvez pas appliquer une réduction qui rend le prix unitaire inférieur au prix fixe de la liste de prix (%s)." % pricelist_item.fixed_price)

                    elif compute_price == 'percentage':
                        pricelist_discounted_price = line.price_unit * (1 - abs(pricelist_item.percent_price) / 100.0)
                        discounted_price = line.price_unit * (1 - abs(line.discount) / 100.0)
                        _logger.info('Line %s: Calculated discounted price is %s with pricelist percentage discount of %s%%.', line.id, discounted_price, pricelist_item.percent_price)
                        if abs(line.discount) > abs(pricelist_item.percent_price) or discounted_price < pricelist_discounted_price:
                            _logger.warning('Line %s: Discount %s%% exceeds pricelist percentage discount %s%% or discounted price %s is less than pricelist discounted price %s.', line.id, abs(line.discount), abs(pricelist_item.percent_price), discounted_price, pricelist_discounted_price)
                            raise ValidationError("Vous ne pouvez pas appliquer une réduction supérieure à la réduction en pourcentage de la liste de prix (%s%%)." % pricelist_item.percent_price)

                    elif compute_price == 'formula':
                        _logger.info('Line %s: Pricelist formula type is used. No validation applied for now.', line.id)
                        # For 'formula' compute_price type, we leave it for now.
                    continue

                max_discount = self._get_max_allowed_discount()
                _logger.info('Line %s: Max allowed discount is %s%%. Current discount is %s%%.', line.id, max_discount, line.discount)
                if abs(line.discount) > abs(max_discount):
                    _logger.warning('Line %s: Discount %s%% exceeds max allowed discount %s%%.', line.id, abs(line.discount), abs(max_discount))
                    raise ValidationError("Vous ne pouvez pas appliquer une réduction supérieure à ce que votre niveau permet (%s%%). Demandez à votre manager pour accorder une réduction supérieure." % max_discount)

    @api.model
    def _get_max_allowed_discount(self):
        max_discount_allowed = self.env['discount.settings'].search_read([
            ('group_ids', 'in', self.env.user.groups_id.ids)
        ], ['max_amount'], order='max_amount DESC', limit=1)
        fallback_value = 999 if self.env.is_admin() else 0
        return max_discount_allowed and max_discount_allowed[0]['max_amount'] or fallback_value


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        copy_order = super(SaleOrder, self.with_context(bypass_max_discount_check=True)).copy(default=default)
        # reduce the non authorized discount amount to max allowed amount
        max_discount = self.env['sale.order.line']._get_max_allowed_discount()
        lines_to_cap = copy_order.order_line.filtered(lambda l: l.discount > max_discount)
        if lines_to_cap:
            lines_to_cap.discount = max_discount
            lines_to_cap.order_id.message_post(body="Ce devis a été copié depuis un devis qui contenait une remise supérieur à %s%%. La remise a donc été réduite au montant maximum autorisé par votre niveau." % max_discount)
        return copy_order

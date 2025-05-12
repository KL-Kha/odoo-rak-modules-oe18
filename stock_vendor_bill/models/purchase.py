from odoo import api, fields, models, _
import json


class Purchase(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line.taxes_id', 'order_line.price_subtotal', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        def compute_taxes(order_line):
            return order_line.taxes_id._origin.compute_all(
                **order_line.with_context(taxes_on_invoiced_qty=True)._prepare_compute_all_values())

        account_move = self.env['account.move']
        for order in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line,
                                                                                         compute_taxes)
            tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
                                                      order.amount_untaxed, order.currency_id)
            order.tax_totals_json = json.dumps(tax_totals)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'qty_invoiced')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(**line._prepare_compute_all_values())
            taxes_on_invoiced_qty = line.taxes_id.compute_all(**line.with_context(taxes_on_invoiced_qty=True)._prepare_compute_all_values())
            line.update({
                'price_tax': taxes_on_invoiced_qty['total_included'] - taxes_on_invoiced_qty['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        self.ensure_one()
        if self._context.get('taxes_on_invoiced_qty'):
            return {
                'price_unit': self.price_unit,
                'currency': self.order_id.currency_id,
                'quantity': self.qty_invoiced,
                'product': self.product_id,
                'partner': self.order_id.partner_id,
            }
        else:
            return {
                'price_unit': self.price_unit,
                'currency': self.order_id.currency_id,
                'quantity': self.product_qty,
                'product': self.product_id,
                'partner': self.order_id.partner_id,
            }
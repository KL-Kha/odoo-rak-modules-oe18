from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account', copy=False)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    fal_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account', copy=False)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account', related='order_id.analytic_account_id', store=True, readonly=False)

    # transfer analytic account to invoice
    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res['analytic_account_id'] = self.fal_analytic_account_id.id or self.order_id.analytic_account_id.id
        return res

class AccountMove(models.Model):
    _inherit = "account.move"

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account', copy=False)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account', copy=False)

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # Transfer analytic account to purchase "_run_buy"
    @api.model
    def _prepare_purchase_order_line_from_procurement(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values, po):
        res = super(PurchaseOrderLine, self)._prepare_purchase_order_line_from_procurement(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values, po)
        move = values.get('move_dest_ids', False)
        sale_line = move and move.sale_line_id
        sale_line_obj = self.env['sale.order.line']
        analytic = False
        if sale_line:
            analytic = sale_line.fal_analytic_account_id.id or sale_line.order_id.analytic_account_id.id
        # for drop shipping
        elif values.get('sale_line_id', False):
            sale_line_id = sale_line_obj.browse(values.get('sale_line_id', False))
            analytic = sale_line_id.fal_analytic_account_id.id or sale_line_id.order_id.analytic_account_id.id
        res['account_analytic_id'] = analytic
        return res


class StockRule(models.Model):
    _inherit = 'stock.rule'

    # update Analytic account
    def _update_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, line):
        res = super(StockRule, self)._update_purchase_order_line(product_id, product_qty, product_uom, company_id, values, line)
        move = values.get('move_dest_ids')
        sale_line = move and move.sale_line_id
        analytic = False
        if sale_line:
            analytic = sale_line.fal_analytic_account_id.id or sale_line.order_id.analytic_account_id.id
        res['account_analytic_id'] = analytic
        return res

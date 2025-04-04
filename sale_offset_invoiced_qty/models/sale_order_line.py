# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    offset_invoiced_qty = fields.Float(string="Offset Invoiced Qty")
    
    
    @api.depends('offset_invoiced_qty','invoice_lines.move_id.state', 'invoice_lines.quantity', 'untaxed_amount_to_invoice')
    def _compute_qty_invoiced(self):
        super(SaleOrderLine, self)._compute_qty_invoiced()
        for line in self:
            line.qty_invoiced += line.offset_invoiced_qty or 0.0
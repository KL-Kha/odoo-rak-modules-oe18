# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    offset_invoiced_qty = fields.Float(string="Offset Invoiced Qty")

    @api.depends('offset_invoiced_qty','invoice_lines.move_id.state', 'invoice_lines.quantity', 'qty_received', 'product_uom_qty', 'order_id.state')
    def _compute_qty_invoiced(self):
        super(PurchaseOrderLine, self)._compute_qty_invoiced()
        for line in self:
            line.qty_invoiced += line.offset_invoiced_qty or 0.0
            line.qty_to_invoice -= line.offset_invoiced_qty or 0.0
            if line.qty_to_invoice < 0:
                line.qty_to_invoice = 0.0

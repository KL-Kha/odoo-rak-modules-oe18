# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    offset_received_qty = fields.Float(string="Offset Received Qty")

    @api.depends('offset_received_qty','move_ids.state', 'move_ids.product_uom_qty', 'move_ids.product_uom')
    def _compute_qty_received(self):
        super(PurchaseOrderLine, self)._compute_qty_received()
        for line in self:
            if line.qty_received_method == 'stock_moves':
                line.qty_received += line.offset_received_qty or 0.0
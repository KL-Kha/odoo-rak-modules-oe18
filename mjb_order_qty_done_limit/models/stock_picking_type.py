from odoo import models, fields

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    x_order_qty_done_limit = fields.One2many('x_order_qty_done_limit', 'x_picking_type_id', string='Picking Quantity Done Limits')

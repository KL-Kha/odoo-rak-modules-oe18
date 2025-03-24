from odoo import models, fields, api


class OrderQtyDoneLimit(models.Model):
    _name = 'x_order_qty_done_limit'
    _description = 'Order Qty Done Limit'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _rec_name = "x_name"

    x_name = fields.Char(string="Name")
    x_picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type')
    x_overcharge_ratio = fields.Float(string='Overcharge Ratio (%)')
    x_is_active = fields.Boolean(string='Is Active')

    _sql_constraints = [
        ('unique_x_picking_type_id', 'UNIQUE(x_picking_type_id)', 'Only one record per operation type is allowed.'),
    ]
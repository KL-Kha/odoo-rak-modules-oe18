
from odoo import api, models, fields



class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    x_studio_pct_date = fields.Date(compute="_onchange_date_planned", default=None,
                                    store=True, readonly=False, string="PCT Date")


    @api.depends('order_id.date_planned')
    def _onchange_date_planned(self):
        for order_line in self:
            if not order_line.x_studio_pct_date and order_line.order_id.date_planned:
                order_line.x_studio_pct_date = order_line.order_id.date_planned.date()


class ReturnPickingLine(models.TransientModel):

    _inherit = "stock.return.picking.line"

    barcode = fields.Char(related="product_id.barcode")
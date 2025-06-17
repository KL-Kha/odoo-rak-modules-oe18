from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends('bill_ids')
    def _compute_bill(self):
        for order in self:
            order.bill_count = len(order.bill_ids)

    bill_ids = fields.Many2many('account.move', 'picking_account_move_rel', 'picking_id', 'move_id', string='Vendor Bills', copy=False)
    bill_count = fields.Integer(compute="_compute_bill", string='Bill Count', copy=False, default=0, store=True)

    def action_view_bills(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        if len(self.bill_ids) > 1:
            result['domain'] = "[('id', 'in', %s)]" % self.bill_ids.ids
        else:
            form_view = self.env.ref('account.view_move_form')
            result['views'] = [(form_view.id, 'form')]
            result['res_id'] = self.bill_ids.id
        return result


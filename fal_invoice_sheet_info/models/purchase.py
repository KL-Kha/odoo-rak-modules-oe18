from odoo import models, api, fields


class PurchaseOrdre(models.Model):
    _inherit = 'purchase.order'

    fal_invoice_paid = fields.Boolean(
        string="Fully Paid",
        compute='get_status_from_line',
        store=True,)

    @api.depends('state', 'invoice_status', 'invoice_ids', 'invoice_ids.payment_state')
    def get_status_from_line(self):
        for po in self:
            if po.state in ['purchase', 'done'] and po.invoice_status == 'invoiced':
                invoice_ids = po.order_line.mapped(
                    'invoice_lines').mapped(
                    'move_id').filtered(
                    lambda r: r.move_type in ['in_invoice', 'in_refund'])
                all_invoice_paid = True
                for invoice in invoice_ids:
                    if invoice.payment_state != 'paid':
                        all_invoice_paid = False
                po.update(
                    {'fal_invoice_paid': all_invoice_paid})
            else:
                po.update(
                    {'fal_invoice_paid': False})

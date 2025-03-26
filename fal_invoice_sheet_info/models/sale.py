from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fal_invoice_paid = fields.Boolean(
        string="Fully Paid",
        compute='get_status_from_line',
        store=True,)

    @api.depends('state', 'invoice_status', 'invoice_ids', 'invoice_ids.payment_state')
    def get_status_from_line(self):
        # If order type == sale order
        # If sale order invoice status is invoiced and all the invoice related to this sale order is on status paid. Then True, else False
        for so in self:
            if so.state in ['sale', 'done'] and so.invoice_status in ['invoiced', 'upselling']:
                invoice_ids = so.order_line.mapped(
                    'invoice_lines').mapped(
                    'move_id').filtered(
                    lambda r: r.move_type in ['out_invoice', 'out_refund'])
                all_invoice_paid = True
                for invoice in invoice_ids:
                    if invoice.payment_state != 'paid':
                        all_invoice_paid = False
                so.update(
                    {'fal_invoice_paid': all_invoice_paid})
            else:
                so.update(
                    {'fal_invoice_paid': False})

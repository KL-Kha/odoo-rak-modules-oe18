from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    amount_to_invoice = fields.Monetary(
        string="Un-Billed Balance",
        compute='_compute_amount_to_bill'
    )
    amount_invoiced = fields.Monetary(
        string="Billed Amount",
        compute='_compute_amount_billed'
    )

    @api.depends('invoice_lines', 'invoice_lines.price_total', 'invoice_lines.move_id.state')
    def _compute_amount_billed(self):
        for line in self:
            amount_invoiced = 0.0
            for invoice_line in line._get_invoice_lines():
                invoice = invoice_line.move_id
                if invoice.state == 'posted':
                    invoice_date = invoice.invoice_date or fields.Date.context_today(self)
                    # Convert the price_total to the currency of the purchase order line
                    amount_invoiced_unsigned = invoice_line.currency_id._convert(
                        invoice_line.price_total, line.currency_id, line.company_id, invoice_date
                    )
                    # Handle direction sign for vendor bills and refunds
                    if invoice.move_type == 'in_invoice':
                        amount_invoiced += amount_invoiced_unsigned
                    elif invoice.move_type == 'in_refund':
                        amount_invoiced -= amount_invoiced_unsigned
            line.amount_invoiced = amount_invoiced

    @api.depends('price_total', 'amount_invoiced')
    def _compute_amount_to_bill(self):
        for line in self:
            # Calculate the amount that is yet to be invoiced
            line.amount_to_invoice = line.price_total - line.amount_invoiced

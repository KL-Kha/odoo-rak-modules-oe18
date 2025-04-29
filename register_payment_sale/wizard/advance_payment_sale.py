from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError

class SaleOrderPayment(models.TransientModel):
    _name = "sale.order.wizard"

    advance_id = fields.Many2one('advance.payment.dorsan')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id')
    currency_id = fields.Many2one('res.currency', related='sale_order_id.currency_id')
    total_register_payment = fields.Monetary('Total Registered Amount', related='sale_order_id.total_register_payment')
    total_request_amount = fields.Monetary('Total Requested Amount', related='sale_order_id.total_request_amount')
    due_amount = fields.Monetary('Due Amount', related='sale_order_id.due_amount')
    # amount_total = fields.Monetary('Total', related='sale_order_id.amount_total')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, tracking=4, related='sale_order_id.amount_total')
    request_amount = fields.Monetary('Request Amount')


class AdvancePaymentDorsan(models.TransientModel):

    _name = 'advance.payment.dorsan'
    _description = 'Sale Advance Payment'

    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')],
                                    tracking=True, readonly=True, default='customer')
    payment_type = fields.Selection(
        [('outbound', 'Send Money'), ('inbound', 'Receive Money'), ('transfer', 'Internal Transfer')],
        string='Payment Type', required=True, readonly=True, default='inbound')

    # def _get_currency_id(self):
    #     return self.env.user.company_id.currency_id

    @api.onchange('sale_order_ids')
    def _compute_currency_id(self):
        for rec in self:
            if not rec.currency_id and rec.sale_order_ids:
                rec.currency_id = rec.sale_order_ids[0].sale_order_id.company_id.currency_id

    journal_id = fields.Many2one('account.journal', string='Account Journal')
    # currency_id = fields.Many2one('res.currency', readonly=False, default=_get_currency_id)
    currency_id = fields.Many2one('res.currency', readonly=False, store=True)
    status = fields.Selection([('draft', 'Draft')], string='Status', default='draft')
    sale_order_ids = fields.One2many('sale.order.wizard', 'advance_id', string='Sale Orders')
    amount = fields.Monetary('Total Request Amount')
    total_payment_amount = fields.Monetary('Total Registered Payment Amount', compute='_get_total_payment_amount')
    total_due_amount = fields.Monetary('Total Due Amount', compute='_get_total_payment_amount')
    receipt = fields.Binary("Receipt")
    memo = fields.Char('Memo')

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        for rec in self:
            if rec.journal_id.currency_id:
                rec.currency_id = rec.journal_id.currency_id

    @api.onchange('sale_order_ids.request_amount', 'sale_order_ids')
    def onchange_order_payment_amount(self):
        request_amount = 0
        for order in self.sale_order_ids:
            request_amount += order.request_amount
        self.amount = request_amount

    def confirm(self):
        partner_id = self.sale_order_ids[0].partner_id.id
        for wizard in self.sale_order_ids:
            if wizard.sale_order_id.due_amount == 0.00:
                raise ValidationError(_(wizard.sale_order_id.name + " : No Amount Due!"))
            if partner_id != wizard.partner_id.id:
                raise ValidationError(_("Please select order for same partner!"))
            if round(wizard.request_amount, 2) > round(wizard.sale_order_id.amount_total, 2):
                raise ValidationError(_("Requested Amount should not be greater then Order Amount!"))
            elif wizard.request_amount == 0.00:
                raise ValidationError(_(wizard.sale_order_id.name + " : Request Amount should not be zero!"))
            elif round(wizard.request_amount, 2) > round(wizard.due_amount - wizard.total_request_amount, 2):
                raise ValidationError(_(wizard.sale_order_id.name + " : Request Amount should not be greater then Order Amount!"))

        if not self.amount:
            raise ValidationError(_("Total Request Amount should not be zero!"))
        payment = self.env['account.payment'].with_context(from_wizard=True).create({
            'payment_type': 'inbound',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'partner_type': 'customer',
            'partner_id': partner_id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'journal_id': self.journal_id.id,
            'receipt': self.receipt,
            'sale_order_ids': [(6, 0, [])],
            'ref': self.memo,
        })
        for wizard in self.sale_order_ids:
            advance_account_payment_ids = wizard.sale_order_id.advance_account_payment_ids.ids
            wizard.sale_order_id.advance_account_payment_ids = [(6, 0, advance_account_payment_ids + [payment.id])]
            self.env['sale.order.payment'].create({
                'payment_id': payment.id,
                'sale_order_id': wizard.sale_order_id.id,
                'request_amount': wizard.request_amount,
                'register_amount': wizard.request_amount})





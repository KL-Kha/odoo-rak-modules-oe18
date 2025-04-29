from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, MissingError
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment.term"

    x_studio_delivery_payments_required = fields.Boolean('Payment Request Required')


class AccountPayment(models.Model):
    _inherit = "account.payment"

    sale_order_ids = fields.One2many('sale.order.payment', 'payment_id', string='Sale Orders', tracking=True)
    payment_number = fields.Char(string='Payment Number', default=lambda x: _('New'), copy=False)
    receipt_attachments = fields.One2many('receipt.account.payment', 'payment_id', string='Receipt')
    request_amount = fields.Monetary('Request Amount')
    order_total_amount = fields.Monetary('Sale Order Total')
    receipt = fields.Binary("Receipt")
    x_studio_finance_appoved = fields.Boolean('Finance Approved', tracking=True)
    is_any_picking_done = fields.Boolean('Is Any Picking Done', compute='_get_picking_done')
    memo = fields.Char('Memo')

    def _get_picking_done(self):
        for rec in self:
            if rec.sale_order_ids:
                picking_ids = rec.sale_order_ids[0].sale_order_id.picking_ids
                if any(picking_ids.filtered(lambda picking: picking.state in ('done'))):
                    rec.is_any_picking_done = True
                else:
                    rec.is_any_picking_done = False
            else:
                rec.is_any_picking_done = False

    def action_draft(self):
        res = super(AccountPayment, self).action_draft()
        for rec in self.sale_order_ids:
            if not self._context.get('is_any_picking_done'):
                rec.sale_order_id.write({'x_studio_finance_appoved': False})
            self.env['mail.message'].create({
                'body': "Finance Approved -> False " + rec.sale_order_id.name,
                'model': 'account.payment',
                'res_id': self.id,
            })
        return res

    def action_cancel(self):
        res = super(AccountPayment, self).action_cancel()
        for rec in self.sale_order_ids:
            # rec.sale_order_id.write({'x_studio_finance_appoved': False,
            #                          'advance_account_payment_ids': [(3, self.id)]})
            rec.sale_order_id.write({'x_studio_finance_appoved': False})
            self.env['mail.message'].create({
                'body': "Finance Approved -> False " + rec.sale_order_id.name,
                'model': 'account.payment',
                'res_id': self.id,
            })
            # rec.unlink()
        return res

    def action_post(self):
        _logger.info("=> action_post")

        res = super(AccountPayment, self).action_post()

        # self // account.payment
        for rec in self.sale_order_ids:
            # rec // sale.order.payment -> self.sale_order_ids[0]
            # rec.payment_id == self
            _logger.info(f"=> [posted] action_post: res.id: {self.id} / due_amount: {rec.due_amount}")

            # NOTE: https://rakwireless.atlassian.net/browse/DEVOPS-392
            # NOTE: https://rakwireless.atlassian.net/browse/DEVOPS-538
            # sale.order.payment -> sale.order
            sale_order = rec.sale_order_id
            payment_term = sale_order.payment_term_id
            global_channel = sale_order.global_channel_id
            amount_total = sale_order.amount_total
            x_studio_require_approval = payment_term.x_studio_require_approval
            x_studio_advance_required = payment_term.x_studio_advance_required
            related_so = sale_order.x_studio_related_so

            percentage_required = float(x_studio_advance_required) / 100.00
            minimum_required = percentage_required * amount_total
            is_finance_approved = rec.total_register_payment >= minimum_required

            _logger.info(f"=> [TRACING] Global channel: {global_channel.name}")
            _logger.info(f"=> [TRACING] percentage_required: {percentage_required}")
            _logger.info(f"=> [TRACING] SO amount_total: {amount_total}")
            _logger.info(f"=> [TRACING] minimum_required: {minimum_required}")

            if global_channel.name == "Offline" and x_studio_require_approval:

                if x_studio_advance_required > 0:
                    if is_finance_approved:
                        # Happy path
                        _logger.info(f"=> [TRACING] Finance approved threshold met! amount due "
                                     f"{rec.total_register_payment} is >= to minimum_required: {minimum_required}")

                        self.env['mail.message'].create({
                            'body': "Finance Approved -> True " + rec.sale_order_id.name,
                            'model': 'account.payment',
                            'res_id': self.id,
                        })
                        rec.sale_order_id.write({'x_studio_finance_appoved': True})

                        _logger.info(
                            f"=> [TRACING] Finance approved > action_post: res.id: {self.id} / Total registered amount: {rec.total_register_payment} / due_amount: {rec.due_amount} / x_studio_finance_appoved: {sale_order.x_studio_finance_appoved}")

                        # NOTE: https://rakwireless.atlassian.net/browse/DEVOPS-405
                        # FIXME: This may cause the UI to timeout?
                        server_action = sale_order.env.ref('mb.rak_multi_orders_sync_fields').sudo().with_context({
                            "payload": {
                                "id": sale_order.id,
                                "model": "sale.order"
                            }
                        })
                        server_action.run()

                        _logger.info(
                            f"=> [TRACING] ir.actions.server {server_action} / sale_order ({sale_order.id}): {sale_order.name}")

                        sales_person = sale_order.user_id
                        sales_person_email = sales_person.login or ""
                        _logger.info(
                            f"=> [TRACING] ir.actions.server {server_action} / sales_person_email: {sales_person_email}")

                        # Ideally we should check `ir_logging.message` before sending out this email.
                        template_id = self.env.ref('account.mail_template_data_payment_receipt_pmc').id
                        email_values = {
                            'email_from': 'no-reply.erp@rakwireless.com',
                            'email_cc': f"{sales_person_email}",
                            'subject': f"#{sale_order.name}, Payment has been approved. 此销售单查款已审批，请知悉并安排发货事项",
                        }
                        email_template = self.env['mail.template'].browse(template_id)

                        try:
                            template_name = email_template.display_name
                            email_template.send_mail(self.id, force_send=True, email_values=email_values)
                        except MissingError as err:
                            _logger.error(
                                f"=> [TRACING] Error fetching email template: {err}"
                            )

                        super(AccountPayment, self).mark_as_sent()
                    else:
                        _logger.info(
                            f"=> [TRACING] Finance approved threshold not met! Total registered amount: {rec.total_register_payment} is lower than minimum_required: {minimum_required}")
                else:
                    _logger.info(
                        f"=> [TRACING] Invalid value! / x_studio_advance_required: {x_studio_advance_required}")
        return res

    @api.model
    def create(self, vals):
        rec = super(AccountPayment, self).create(vals)
        if rec.partner_type == 'customer':
            payment_number = self.env['ir.sequence'].next_by_code('account.payment.number')
            rec.payment_number = payment_number
        return rec

    @api.onchange('sale_order_ids.register_amount', 'sale_order_ids')
    def onchange_sale_order_ids(self):
        for rec in self:
            amount = 0
            for order in rec.sale_order_ids:
                amount += order.register_amount

            rec.amount = amount

    def write(self, vals):
        res = super(AccountPayment, self).write(vals)
        partner_id = self.partner_id
        if not self._context.get('from_wizard'):
            for order in self.sale_order_ids:
                # if order.sale_order_id.due_amount == 0.00:
                #     raise ValidationError(_(order.sale_order_id.name + " : No Amount Due!"))
                if partner_id.id != order.partner_id.id:
                    raise ValidationError(_("Please select order for same partner!"))

                # NOTE Removed for https://rakwireless.atlassian.net/browse/DEVOPS-560
                # if round(order.register_amount, 2) > order.sale_order_id.amount_total:
                #     raise ValidationError(_("Register Amount should not be greater then Order Amount!"))

                if order.register_amount == 0.00:
                    raise ValidationError(_(order.sale_order_id.name + " : Register Amount should not be zero!"))

                if self.id not in order.sale_order_id.advance_account_payment_ids.ids:
                    order.sale_order_id.advance_account_payment_ids = [(4, self.id)]
        return res


class SaleOrderPayment(models.Model):
    _name = "sale.order.payment"

    payment_id = fields.Many2one('account.payment', string='Payment')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_id')
    currency_id = fields.Many2one('res.currency', related='sale_order_id.currency_id')
    total_register_payment = fields.Monetary('Total Registered Amount', related='sale_order_id.total_register_payment')
    total_request_amount = fields.Monetary('Total Requested Amount', related='sale_order_id.total_request_amount')
    due_amount = fields.Monetary('Due Amount', related='sale_order_id.due_amount')
    # amount_total = fields.Monetary('Total', related='sale_order_id.amount_total')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, tracking=4,
                                   related='sale_order_id.amount_total')
    request_amount = fields.Monetary('Request Amount')
    register_amount = fields.Monetary('Register Amount')

    def write(self, vals):
        _logger.info("=> sale.order.payment -> write")

        old_sale_order_id = self.sale_order_id
        res = super(SaleOrderPayment, self).write(vals)
        old_sale_order_id.advance_account_payment_ids = [(3, self.payment_id.id)]
        old_sale_order_id._get_total_register_payment()
        return res

    def unlink(self):
        if self.sale_order_id:
            self.sale_order_id.advance_account_payment_ids = [(3, self.payment_id.id)]
            self.sale_order_id._get_total_register_payment()
        return super(SaleOrderPayment, self).unlink()


class Receipt(models.Model):
    _name = "receipt.account.payment"

    name = fields.Char('Receipt Description')
    receipt = fields.Binary('Receipt')
    payment_id = fields.Many2one('account.payment', string='Payment')

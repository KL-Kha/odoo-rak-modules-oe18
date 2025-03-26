# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict


class purchaseAdvancePaymentInv(models.TransientModel):
    _name = 'purchase.advance.payment.inv'
    _description = "purchases Advance Payment Bill"

    advance_payment_method = fields.Selection(
        selection=[
            ('delivered', "Regular bill"),
            ('percentage', "Down payment (percentage)"),
            ('fixed', "Down payment (fixed amount)"),
        ],
        string="Create Bill",
        default='delivered',
        required=True,
        help="A standard bill is issued with all the order lines ready for invoicing,"
            "according to their invoicing policy (based on ordered or delivered quantity).")
    count = fields.Integer(string="Order Count", compute='_compute_count')
    purchase_order_ids = fields.Many2many(
        'purchase.order', default=lambda self: self.env.context.get('active_ids'))

    # Down Payment logic
    has_down_payments = fields.Boolean(
        string="Has down payments", compute="_compute_has_down_payments")
    deduct_down_payments = fields.Boolean(string="Deduct down payments", default=True)

    # New Down Payment
    amount = fields.Float(
        string="Down Payment",
        help="The percentage of amount to be billed in advance.")
    fixed_amount = fields.Monetary(
        string="Down Payment Amount (Fixed)",
        help="The fixed amount to be billed in advance.")
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
        store=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        compute='_compute_company_id',
        store=True)
    amount_invoiced = fields.Monetary(
        string="Already billed",
        compute="_compute_bill_amounts",
        help="Only confirmed down payments are considered.")
    amount_to_invoice = fields.Monetary(
        string="Amount to bill",
        compute="_compute_bill_amounts",
        help="The amount to bill = purchase Order Total - Confirmed Down Payments.")

    # UI
    display_draft_invoice_warning = fields.Boolean(compute="_compute_display_draft_invoice_warning")
    display_invoice_amount_warning = fields.Boolean(compute="_compute_display_invoice_amount_warning")
    consolidated_billing = fields.Boolean(
        string="Consolidated Billing", default=True,
        help="Create one bill for all orders related to same customer and same invoicing address"
    )

    #=== COMPUTE METHODS ===#

    @api.depends('purchase_order_ids')
    def _compute_count(self):
        for wizard in self:
            wizard.count = len(wizard.purchase_order_ids)

    @api.depends('purchase_order_ids')
    def _compute_has_down_payments(self):
        for wizard in self:
            wizard.has_down_payments = bool(
                wizard.purchase_order_ids.order_line.filtered('is_downpayment')
            )

    # next computed fields are only used for down payments invoices and therefore should only
    # have a value when 1 unique SO is invoiced through the wizard
    @api.depends('purchase_order_ids')
    def _compute_currency_id(self):
        self.currency_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.currency_id = wizard.purchase_order_ids.currency_id

    @api.depends('purchase_order_ids')
    def _compute_company_id(self):
        self.company_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.company_id = wizard.purchase_order_ids.company_id

    @api.depends('amount', 'fixed_amount', 'advance_payment_method', 'amount_to_invoice')
    def _compute_display_invoice_amount_warning(self):
        for wizard in self:
            invoice_amount = wizard.fixed_amount
            if wizard.advance_payment_method == 'percentage':
                invoice_amount = wizard.amount / 100 * sum(wizard.purchase_order_ids.mapped('amount_total'))
            wizard.display_invoice_amount_warning = invoice_amount > wizard.amount_to_invoice

    @api.depends('purchase_order_ids')
    def _compute_display_draft_invoice_warning(self):
        for wizard in self:
            wizard.display_draft_invoice_warning = wizard.purchase_order_ids.invoice_ids.filtered(lambda invoice: invoice.state == 'draft')

    @api.depends('purchase_order_ids')
    def _compute_bill_amounts(self):
        for wizard in self:
            wizard.amount_invoiced = sum(wizard.purchase_order_ids._origin.mapped('amount_invoiced'))
            wizard.amount_to_invoice = sum(wizard.purchase_order_ids._origin.mapped('amount_to_invoice'))

    #=== ONCHANGE METHODS ===#

    @api.onchange('advance_payment_method')
    def _onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            amount = self.default_get(['amount']).get('amount')
            return {'value': {'amount': amount}}

    #=== CONSTRAINT METHODS ===#

    def _check_amount_is_positive(self):
        for wizard in self:
            if wizard.advance_payment_method == 'percentage' and wizard.amount <= 0.00:
                raise UserError(_('The value of the down payment amount must be positive.'))
            elif wizard.advance_payment_method == 'fixed' and wizard.fixed_amount <= 0.00:
                raise UserError(_('The value of the down payment amount must be positive.'))

    #=== ACTION METHODS ===#

    def create_invoices(self):
        self._check_amount_is_positive()
        invoices = self._create_invoices(self.purchase_order_ids)
        return self.purchase_order_ids.action_view_invoice(invoices=invoices)

    def view_draft_invoices(self):
        return {
            'name': _('Draft Bills'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'views': [(False, 'list'), (False, 'form')],
            'res_model': 'account.move',
            'domain': [('line_ids.purchase_line_ids.order_id', 'in', self.purchase_order_ids.ids), ('state', '=', 'draft')],
        }

    #=== BUSINESS METHODS ===#

    def _create_invoices(self, purchase_orders):
        self.ensure_one()
        if self.advance_payment_method == 'delivered':
            return purchase_orders._create_invoices(final=self.deduct_down_payments, grouped=not self.consolidated_billing)
        else:
            self.purchase_order_ids.ensure_one()
            self = self.with_company(self.company_id)
            order = self.purchase_order_ids

            # Create down payment section if necessary
            purchaseOrderline = self.env['purchase.order.line'].with_context(purchase_no_log_for_new_lines=True)
            if not any(line.display_type and line.is_downpayment for line in order.order_line):
                purchaseOrderline.create(
                    self._prepare_down_payment_section_values(order)
                )

            values, accounts = self._prepare_down_payment_lines_values(order)
            down_payment_lines = purchaseOrderline.create(values)

            invoice = self.env['account.move'].sudo().create(
                self._prepare_invoice_values(order, down_payment_lines)
            )

            # Ensure the invoice total is exactly the expected fixed amount.
            if self.advance_payment_method == 'fixed':
                delta_amount = (invoice.amount_total - self.fixed_amount) * (1 if invoice.is_inbound() else -1)
                if not order.currency_id.is_zero(delta_amount):
                    receivable_line = invoice.line_ids\
                        .filtered(lambda aml: aml.account_id.account_type == 'liability_payable')[:1]
                    product_lines = invoice.line_ids\
                        .filtered(lambda aml: aml.display_type == 'product')
                    tax_lines = invoice.line_ids\
                        .filtered(lambda aml: aml.tax_line_id.amount_type not in (False, 'fixed'))

                    if product_lines and tax_lines and receivable_line:
                        line_commands = [Command.update(receivable_line.id, {
                            'amount_currency': receivable_line.amount_currency + delta_amount,
                        })]
                        delta_sign = 1 if delta_amount > 0 else -1
                        for lines, attr, sign in (
                            (product_lines, 'price_total', -1),
                            (tax_lines, 'amount_currency', 1),
                        ):
                            remaining = delta_amount
                            lines_len = len(lines)
                            for line in lines:
                                if order.currency_id.compare_amounts(remaining, 0) != delta_sign:
                                    break
                                amt = delta_sign * max(
                                    order.currency_id.rounding,
                                    abs(order.currency_id.round(remaining / lines_len)),
                                )
                                remaining -= amt
                                line_commands.append(Command.update(line.id, {attr: line[attr] + amt * sign}))
                        invoice.line_ids = line_commands

            # Unsudo the invoice after creation if not already sudoed
            invoice = invoice.sudo(self.env.su)

            poster = self.env.user._is_internal() and self.env.user.id or SUPERUSER_ID
            invoice.with_user(poster).message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': invoice, 'origin': order},
                subtype_xmlid='mail.mt_note',
            )

            title = _("Down payment Bill")
            order.with_user(poster).message_post(
                body=_("%s has been created", invoice._get_html_link(title=title)),
            )

            return invoice

    def _prepare_down_payment_section_values(self, order):
        return {
            "name": "Down payment",
            'product_qty': 0.0,
            'order_id': order.id,
            'display_type': 'line_section',
            'is_downpayment': True,
            'sequence': order.order_line and order.order_line[-1].sequence + 1 or 10,
        }

    def _prepare_down_payment_lines_values(self, order):
        """ Create one down payment line per tax or unique taxes combination and per account.
            Apply the tax(es) to their respective lines.

            :param order: Order for which the down payment lines are created.
            :return:      An array of dicts with the down payment lines values.
        """
        self.ensure_one()
        AccountTax = self.env['account.tax']

        if self.advance_payment_method == 'percentage':
            ratio = self.amount / 100
        else:
            ratio = self.fixed_amount / order.amount_total if order.amount_total else 1

        order_lines = order.order_line.filtered(lambda l: not l.display_type and not l.is_downpayment)
        down_payment_values = []
        for line in order_lines:
            base_line_values = line._prepare_base_line_for_taxes_computation()
            product_account = line['product_id'].product_tmpl_id.get_product_accounts(fiscal_pos=order.fiscal_position_id)
            account = product_account.get('downpayment') or product_account.get('income')
            AccountTax._add_tax_details_in_base_line(base_line_values, order.company_id)
            tax_details = base_line_values['tax_details']

            taxes = line.taxes_id.flatten_taxes_hierarchy()
            fixed_taxes = taxes.filtered(lambda tax: tax.amount_type == 'fixed')
            down_payment_values.append([
                taxes - fixed_taxes,
                base_line_values['analytic_distribution'],
                tax_details['raw_total_excluded_currency'],
                account,
            ])
            for fixed_tax in fixed_taxes:
                if fixed_tax.price_include:
                    continue

                if fixed_tax.include_base_amount:
                    pct_tax = taxes[list(taxes).index(fixed_tax) + 1:]\
                        .filtered(lambda t: t.is_base_affected and t.amount_type != 'fixed')
                else:
                    pct_tax = self.env['account.tax']
                down_payment_values.append([
                    pct_tax,
                    base_line_values['analytic_distribution'],
                    base_line_values['quantity'] * fixed_tax.amount,
                    account
                ])

        downpayment_line_map = {}
        analytic_map = {}
        base_downpayment_lines_values = self._prepare_base_downpayment_line_values(order)
        for tax_id, analytic_distribution, price_subtotal, account in down_payment_values:
            grouping_key = {
                'taxes_id': tuple(sorted(tax_id.ids)),
                'account_id': account,
            }
            grouping_key_tuple = tuple(sorted(grouping_key.items()))
            downpayment_line_map.setdefault(grouping_key_tuple, {
                **base_downpayment_lines_values,
                'taxes_id': grouping_key['taxes_id'],
                'product_qty': 0.0,
                'price_unit': 0.0,
            })
            downpayment_line_map[grouping_key_tuple]['price_unit'] += price_subtotal
            if analytic_distribution:
                analytic_map.setdefault(grouping_key_tuple, [])
                analytic_map[grouping_key_tuple].append((price_subtotal, analytic_distribution))

        lines_values = []
        accounts = []
        for key_tuple, line_vals in downpayment_line_map.items():
            if order.currency_id.is_zero(line_vals['price_unit']):
                continue
            if analytic_map.get(key_tuple):
                line_analytic_distribution = {}
                for price_subtotal, account_distribution in analytic_map[key_tuple]:
                    for account, distribution in account_distribution.items():
                        line_analytic_distribution.setdefault(account, 0.0)
                        line_analytic_distribution[account] += price_subtotal / line_vals['price_unit'] * distribution
                line_vals['analytic_distribution'] = line_analytic_distribution
            line_vals['price_unit'] = order.currency_id.round(line_vals['price_unit'] * ratio)

            lines_values.append(line_vals)
            accounts.append(dict(key_tuple)['account_id'])

        return lines_values, accounts


    def _prepare_base_downpayment_line_values(self, order):
        self.ensure_one()
        return {
            'name': _('Down Payment'),
            'product_qty': 0.0,
            'order_id': order.id,
            'discount': 0.0,
            'is_downpayment': True,
            'sequence': order.order_line and order.order_line[-1].sequence + 1 or 10,
        }

    def _prepare_invoice_values(self, order, po_lines):
        self.ensure_one()
        return {
            **order._prepare_invoice(),
            'invoice_line_ids': [
                Command.create({
                    **line._prepare_account_move_line(),
                    'quantity': 1.0  # Set the default quantity to 1
                })
                for line in po_lines
            ],
        }

    def _get_down_payment_description(self, order):
        self.ensure_one()
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            name = _("Down payment of %s%%", self.amount)
        else:
            name = _('Down Payment')
        del context
        return name

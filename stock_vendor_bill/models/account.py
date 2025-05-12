from odoo import fields, models, api, _
from odoo.exceptions import UserError
import time

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_write_off = fields.Boolean('Is Write Off Line')

    def _create_writeoff(self, writeoff_vals):
        def compute_writeoff_counterpart_vals(values):
            line_values = values.copy()
            line_values['debit'], line_values['credit'] = line_values['credit'], line_values['debit']
            if 'amount_currency' in values:
                line_values['amount_currency'] = -line_values['amount_currency']
            return line_values

        # Group writeoff_vals by journals
        writeoff_dict = {}
        for val in writeoff_vals:
            journal_id = val.get('journal_id', False)
            if not writeoff_dict.get(journal_id, False):
                writeoff_dict[journal_id] = [val]
            else:
                writeoff_dict[journal_id].append(val)

        partner_id = self.env['res.partner']._find_accounting_partner(self[0].partner_id).id
        company_currency = self[0].account_id.company_id.currency_id
        writeoff_currency = self[0].account_id.currency_id or company_currency
        line_to_reconcile = self.env['account.move.line']
        # Iterate and create one writeoff by journal
        writeoff_moves = self.env['account.move']
        for journal_id, lines in writeoff_dict.items():
            total = 0
            total_currency = 0
            writeoff_lines = []
            date = fields.Date.today()
            for vals in lines:
                # Check and complete vals
                if 'account_id' not in vals or 'journal_id' not in vals:
                    raise UserError(_("It is mandatory to specify an account and a journal to create a write-off."))
                if ('debit' in vals) ^ ('credit' in vals):
                    raise UserError(_("Either pass both debit and credit or none."))
                if 'date' not in vals:
                    vals['date'] = self._context.get('date_p') or fields.Date.today()
                vals['date'] = fields.Date.to_date(vals['date'])
                if vals['date'] and vals['date'] < date:
                    date = vals['date']
                if 'name' not in vals:
                    vals['name'] = self._context.get('comment') or _('Write-Off')
                if 'analytic_account_id' not in vals:
                    vals['analytic_account_id'] = self.env.context.get('analytic_id', False)
                # compute the writeoff amount if not given
                if 'credit' not in vals and 'debit' not in vals:
                    amount = sum([r.amount_residual for r in self])
                    vals['credit'] = amount > 0 and amount or 0.0
                    vals['debit'] = amount < 0 and abs(amount) or 0.0
                vals['partner_id'] = partner_id
                total += vals['debit'] - vals['credit']
                if 'amount_currency' not in vals and writeoff_currency != company_currency:
                    vals['currency_id'] = writeoff_currency.id
                    sign = 1 if vals['debit'] > 0 else -1
                    vals['amount_currency'] = sign * abs(sum([r.amount_residual_currency for r in self]))
                    total_currency += vals['amount_currency']

                writeoff_lines.append(compute_writeoff_counterpart_vals(vals))

            # Create balance line
            writeoff_lines.append({
                'name': _('Write-Off'),
                'debit': total > 0 and total or 0.0,
                'credit': total < 0 and -total or 0.0,
                'amount_currency': total_currency,
                'currency_id': total_currency and writeoff_currency.id or False,
                'journal_id': journal_id,
                'account_id': self[0].account_id.id,
                'partner_id': partner_id,
                'is_write_off': True
            })

            # Create the move
            if total != 0.00:

                if self.env.context.get('is_bill_picking_reconcile'):
                    writeoff_move = self.env['account.move'].create({
                        'journal_id': journal_id,
                        'type': 'entry',
                        'date': date,
                        'state': 'draft',
                        'line_ids': [(0, 0, line) for line in writeoff_lines],
                    })
                else:
                    writeoff_move = self.env['account.move'].create({
                        'journal_id': journal_id,
                        'date': date,
                        'state': 'draft',
                        'line_ids': [(0, 0, line) for line in writeoff_lines],
                    })
                writeoff_moves += writeoff_move
                line_to_reconcile += writeoff_move.line_ids.filtered(lambda r: r.account_id == self[0].account_id).sorted(
                    key='id')[-1:]

            # post all the writeoff moves at once
            if writeoff_moves:
                valuation_line_ids = self.env.context.get('valuation_line_ids')
                if valuation_line_ids:
                    for move in writeoff_moves:
                        for move_line in move.line_ids:
                            move_line.product_id = valuation_line_ids[0].product_id.id
                            move_line.name = valuation_line_ids[0].name
                            move_line.quantity = self.env.context.get('qty')
                writeoff_moves.post()

            # Return the writeoff move.line which is to be reconciled
            if self.env.context.get('move_id'):
                base_move_id = self.env.context.get('move_id')
                for move_line in line_to_reconcile:
                    base_move_id.picking_reconciled_line_ids = [(4, move_line.id)]
        return line_to_reconcile


class AccountMove(models.Model):
    _inherit = "account.move"

    picking_reconciled_line_ids = fields.Many2many('account.move.line', 'account_move_account_move_rel', 'bill_id', 'line_id', string="Reconciled line with picking")
    picking_ids = fields.Many2many('stock.picking', 'account_move_picking_rel', 'move_id', 'picking_id', string='Picking')
    po_id = fields.Many2one('purchase.order', string='Purchase Order')

    # def button_draft(self):
    #     res = super(AccountMove, self).button_draft()
    #     writeoff_lines = self.picking_reconciled_line_ids.filtered(lambda line: line.is_write_off == True)
    #     for move_id in writeoff_lines.mapped('move_id'):
    #         if move_id.state != 'cancel':
    #             move_id.button_draft()
    #     return res

    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        writeoff_lines = self.picking_reconciled_line_ids.filtered(lambda line: line.is_write_off == True)
        for move_id in writeoff_lines.mapped('move_id'):
            move_id.button_cancel()
        return res

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.picking_ids:
            # if not self.picking_reconciled_line_ids:
            self.action_create_reconcile()
            self.picking_reconciled_line_ids.write({'reconciled': False})
            if any(not line.full_reconcile_id for line in self.picking_reconciled_line_ids):
                self.picking_reconciled_line_ids.reconcile()

        return res

    def create_write_off(self, valuation_line, picking_reconciled_line_ids):
        total_credit = 0
        total_debit = 0
        writeoff_acc_id = valuation_line.product_id.categ_id.property_account_creditor_price_difference_categ
        writeoff_journal_id = valuation_line.product_id.categ_id.property_stock_journal
        writeoff_lines = []
        for lne in picking_reconciled_line_ids:
            if lne.credit:
                total_credit += lne.credit
            if lne.debit:
                total_debit += lne.debit
        if total_debit != total_credit:
            if total_debit > total_credit:
                # Create balance line
                writeoff_lines.append({
                    'name': _('Write-Off'),
                    'debit': 0.0,
                    'credit': total_debit - total_credit,
                    'journal_id': writeoff_journal_id.id,
                    'account_id': picking_reconciled_line_ids[0].account_id.id,
                    'partner_id': self.partner_id.id,
                    'is_write_off': True
                })
                writeoff_lines.append({
                    'name': _('Write-Off'),
                    'debit': total_debit - total_credit,
                    'credit': 0.0,
                    'journal_id': writeoff_journal_id.id,
                    'account_id': writeoff_acc_id.id,
                    'partner_id': self.partner_id.id,
                })
            elif total_debit < total_credit:
                # Create balance line
                writeoff_lines.append({
                    'name': _('Write-Off'),
                    'debit': total_credit - total_debit,
                    'credit': 0.0,
                    'journal_id': writeoff_journal_id.id,
                    'account_id': picking_reconciled_line_ids[0].account_id.id,
                    'is_write_off': True,
                    'partner_id': self.partner_id.id,
                })
                writeoff_lines.append({
                    'name': _('Write-Off'),
                    'debit': 0.0,
                    'credit': total_credit - total_debit,
                    'journal_id': writeoff_journal_id.id,
                    'account_id': writeoff_acc_id.id,
                    'partner_id': self.partner_id.id,
                })
            date = fields.Date.today()
            writeoff_move = self.env['account.move'].create({
                'journal_id': writeoff_journal_id.id,
                'move_type': 'entry',
                'date': date,
                'state': 'draft',
                'line_ids': [(0, 0, line) for line in writeoff_lines],
                'partner_id': self.partner_id.id,
            })
            writeoff_move.action_post()
            self.picking_reconciled_line_ids = [(4, writeoff_move.line_ids.filtered(lambda x: x.is_write_off)[0].id)]

    def action_create_reconcile(self):
        self.ensure_one()
        self._cr.execute("SELECT picking_id FROM picking_account_move_rel WHERE move_id = " + str(self.id))
        result = self._cr.fetchall()
        stock_picking_ids = []
        for stock_picking in result:
            stock_picking_ids.append(stock_picking[0])

        stock_picking_ids = self.env['stock.picking'].browse(stock_picking_ids)

        scraps = self.env['stock.scrap'].search([('picking_id', 'in', stock_picking_ids.ids)])

        move_lines = self.env['stock.move']
        for picking in stock_picking_ids:
            move_lines += picking.move_lines

        domain = [('id', 'in', (move_lines + scraps.move_id).stock_valuation_layer_ids.ids)]
        stock_valuation_layer_ids = self.env['stock.valuation.layer'].search(domain)

        valuation_account_moves = self.env['account.move']

        for layer in stock_valuation_layer_ids:
            valuation_account_moves += layer.account_move_id

        accounts = valuation_account_moves.mapped('line_ids.account_id')
        bill_line_ids = self.env['account.move.line']
        valuation_line_ids = self.env['account.move.line']
        for account in accounts:
            bill_line_ids += (self.line_ids).filtered(lambda line: line.account_id == account and line.balance)

        for bill_account in bill_line_ids.mapped('account_id'):
            valuation_line_ids += (valuation_account_moves.line_ids).filtered(lambda line: line.account_id == bill_account and line.balance)

        if bill_line_ids and valuation_line_ids:
            writeoff_lines = self.picking_reconciled_line_ids.filtered(lambda line: line.is_write_off==True)
            for move_id in writeoff_lines.mapped('move_id'):
                move_id.button_draft()
                move_id.button_cancel()
            for writeoff_line in writeoff_lines:
                writeoff_line.reconciled = False
                self.picking_reconciled_line_ids = [(3, writeoff_line.id)]

            for line_recon in bill_line_ids+ valuation_line_ids:
                self.picking_reconciled_line_ids = [(4, line_recon.id)]

            additional_bill_line_ids = self.env['account.move.line']

            for bill_line in bill_line_ids:
                for valuation_line in valuation_line_ids:
                    if bill_line.product_id.id == valuation_line.product_id.id:
                        if not bill_line.reconciled or not valuation_line.reconciled:
                            total_billed_qty = 0
                            write_offline= self.env['account.move.line']
                            for account_move_line in self.env['account.move.line'].search([
                                                                    ('purchase_line_id', '=', bill_line.purchase_line_id.id),
                                                                    # ('reconciled', '=', False),
                                                                    ('exclude_from_invoice_tab', '=', False),
                                                                    ('parent_state', '=', 'posted')
                                                                ]):
                                account_move_line.reconciled = False
                                if valuation_line.move_id.stock_move_id.picking_id.id in account_move_line.move_id.picking_ids.ids:
                                    total_billed_qty += account_move_line.quantity
                                    write_offline += account_move_line
                            if total_billed_qty == valuation_line.quantity:
                                reconcilable_additional_bill_line_ids = write_offline.filtered(lambda p: p.reconciled != True)
                                if valuation_line.reconciled == False:
                                    self.create_write_off(valuation_line, reconcilable_additional_bill_line_ids + valuation_line)

            recon_additional_bill_line_ids = self.env['account.move.line'].search([
                ('purchase_line_id.order_id', '=', bill_line_ids[0].purchase_line_id.order_id.id),
                ('full_reconcile_id', '=', False),
                ('parent_state', '=', 'posted')])
            # reconcialable_move_lines = additional_bill_line_ids + valuation_line_ids
            if not recon_additional_bill_line_ids:
                recon_additional_bill_line_ids = additional_bill_line_ids

            for move_line in recon_additional_bill_line_ids + valuation_line_ids:
                for move in additional_bill_line_ids.mapped('move_id'):
                    move.picking_reconciled_line_ids = [(4, move_line.id)]





class PurchaseAdvancePaymentInv(models.TransientModel):
    _inherit = "purchase.advance.payment.inv"

    def _get_default_pickings(self):
        purchase_order_id = self.env['purchase.order'].browse(self.env.context['active_ids'])
        picking_ids = self.env['stock.picking'].search([('id', 'in', purchase_order_id.picking_ids.ids),
                                                        ('state', '=', 'done'),
                                                        ('picking_type_id.code', '=', 'incoming'),
                                                        ('bill_ids', '=', False)])
        return [(6,0,picking_ids.ids)]

    def _get_default_is_picking(self):

        active_ids = self.env.context.get('active_ids')
        if active_ids:
            purchase_order_id = self.env['purchase.order'].browse(active_ids)
            all_picking_ids = self.env['stock.picking'].search([('id', 'in', purchase_order_id.picking_ids.ids),
                                                                ('picking_type_id.code', '=', 'incoming')])
            if not all_picking_ids:
                return False
            else:
                return True
        else:
            return False

    picking_ids = fields.Many2many('stock.picking', string='Pickings', default=_get_default_pickings)
    is_picking = fields.Boolean(string='Is Picking', default=_get_default_is_picking)


    @api.onchange('picking_ids')
    def onchange_picking_ids(self):
        purchase_order_id = self.env['purchase.order'].browse(self.env.context['active_ids'])
        return {'domain': {'picking_ids': [('id', 'in', purchase_order_id.picking_ids.ids),
                                           ('state', '=', 'done'),
                                           ('picking_type_id.code', '=', 'incoming')]}}

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        res = super(PurchaseAdvancePaymentInv, self).onchange_advance_payment_method()
        if self.advance_payment_method == 'received':
            purchase_order_id = self.env['purchase.order'].browse(self.env.context['active_ids'])
            picking_ids = self.env['stock.picking'].search([('id', 'in', purchase_order_id.picking_ids.ids),
                                                            ('state', '=', 'done'),
                                                            ('picking_type_id.code', '=', 'incoming'),
                                                            ('bill_ids', '=', False)])
            self.picking_ids = [(6,0,picking_ids.ids)]
        return res

    def create_invoices(self):
        purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))
        if any(line.product_id.detailed_type == 'service' for line in purchase_orders.order_line) and not self.picking_ids:
            return super(PurchaseAdvancePaymentInv, self).create_invoices()
        if not self.is_picking:
            return super(PurchaseAdvancePaymentInv, self).create_invoices()

        if not self.picking_ids:
            raise UserError(("Please Select Picking!"))

        purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))
        if self.advance_payment_method == 'received':
            invoice = purchase_orders.with_context(journal_id=self.journal_id)._create_invoices(final=self.deduct_down_payments)
            purchase_qty_list = []
            for picking in self.picking_ids:
                for stock_move in picking.move_ids_without_package:
                    if any(stock_move.purchase_line_id.id in purchase_id for purchase_id in purchase_qty_list):
                        for purchase_id_dict in purchase_qty_list:
                            if stock_move.purchase_line_id.id in purchase_id_dict:
                                purchase_id_dict.update({stock_move.purchase_line_id.id: purchase_id_dict.get(stock_move.purchase_line_id.id) + stock_move.quantity_done})
                    else:
                        purchase_qty_list.append({stock_move.purchase_line_id.id: stock_move.quantity_done})
            for invoice_line in invoice.invoice_line_ids:
                available_invoice = False
                for purchase_id_dict in purchase_qty_list:
                    if invoice_line.purchase_line_id.id in purchase_id_dict:
                        available_invoice = True
                        invoice_line.with_context(check_move_validity=False).write({'quantity': purchase_id_dict.get(invoice_line.purchase_line_id.id)})
                if not available_invoice:
                    invoice_line.with_context(check_move_validity=False).write(
                        {'quantity': 0})
                    invoice_line.move_id.with_context(check_move_validity=False)._onchange_currency()
            invoice.with_context(check_move_validity=False)._onchange_currency()

            for picking in self.picking_ids:
                picking.bill_ids = [(4, invoice.id)]
                invoice.picking_ids= [(4, picking.id)]
                invoice.po_id = purchase_orders.id

            for invoice_line in invoice.invoice_line_ids:
                if not invoice_line.quantity:
                    invoice_line.unlink()
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('fal_purchase_downpayment.fal_deposit_product_id',
                                                                 self.product_id.id)

            purchase_line_obj = self.env['purchase.order.line']
            for order in purchase_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.fixed_amount
                if self.product_id.purchase_method != 'purchase':
                    raise UserError(
                        _('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(
                        _("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.supplier_taxes_id.filtered(
                    lambda r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_id).ids
                else:
                    tax_ids = taxes.ids
                context = {'lang': order.partner_id.lang}
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
                po_line = purchase_line_obj.create({
                    'name': _('Down Payment: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'date_planned': order.date_planned or order.date_order,
                    'product_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'analytic_tag_ids': analytic_tag_ids,
                    'taxes_id': [(6, 0, tax_ids)],
                    'fal_is_downpayment': True,
                })
                del context
                invoice = self._create_invoice(order, po_line, amount)
                for picking in self.picking_ids:
                    picking.bill_ids = [(4, invoice.id)]
                    invoice.picking_ids = [(4, picking.id)]
        if self._context.get('open_invoices', False):
            return purchase_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

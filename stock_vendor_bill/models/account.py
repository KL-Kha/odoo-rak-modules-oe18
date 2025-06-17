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
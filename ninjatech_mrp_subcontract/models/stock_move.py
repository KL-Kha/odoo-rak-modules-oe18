from odoo import models, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _account_entry_move(self, qty, description, svl_id, cost):
        """ Accounting Valuation Entries """
        self.ensure_one()
        am_vals = []
        if not self.product_id.is_storable:
            # no stock valuation for consumable products
            return am_vals
        if self._should_exclude_for_valuation():
            # if the move isn't owned by the company, we don't make any valuation
            return am_vals

        move_directions = self.env.context.get('move_directions') or False

        self_is_out_move = self_is_in_move = False
        if move_directions:
            self_is_out_move = move_directions.get(self.id) and 'out' in move_directions.get(self.id)
            self_is_in_move = move_directions.get(self.id) and 'in' in move_directions.get(self.id)
        else:
            self_is_out_move = self._is_out()
            self_is_in_move = self._is_in()

        company_from = self_is_out_move and self.mapped('move_line_ids.location_id.company_id') or False
        company_to = self_is_in_move and self.mapped('move_line_ids.location_dest_id.company_id') or False

        production_id = self.env['mrp.production'].search([("name", '=', self.origin)])
        # is_subcontract = production_id and production_id.x_studio_sourcing.x_studio_order_type == "Subcontracting"

        valuation_vals = self._get_accounting_data_for_valuation()
        journal_id = acc_src = acc_dest = acc_valuation = acc_subcontract_valuation = False
        if len(valuation_vals) > 4:
            journal_id, acc_src, acc_dest, acc_valuation, acc_subcontract_valuation = valuation_vals
        else:
            journal_id, acc_src, acc_dest, acc_valuation = valuation_vals

        # Create Journal Entry for products arriving in the company; in case of routes making the link between several
        # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        if self._is_in():
            if self._is_returned(valued_type='in'):
                am_vals.append(self.with_company(company_to)._prepare_account_move_vals(
                    acc_dest, acc_valuation, journal_id, qty, description, svl_id, cost))
            else:
                if acc_subcontract_valuation:
                    am_vals.append(self.with_company(company_to)._prepare_account_move_vals(
                        acc_src, acc_valuation, journal_id, qty, description, svl_id, cost,
                        acc_subcontract_valuation))
                else:
                    am_vals.append(self.with_company(company_to)._prepare_account_move_vals(
                        acc_src, acc_valuation, journal_id, qty, description, svl_id, cost))

        # Create Journal Entry for products leaving the company
        if self._is_out():
            cost = -1 * cost
            if self._is_returned(valued_type='out'):
                am_vals.append(self.with_company(company_from)._prepare_account_move_vals(
                    acc_valuation, acc_src, journal_id, qty, description, svl_id, cost))
            else:
                am_vals.append(self.with_company(company_from)._prepare_account_move_vals(
                    acc_valuation, acc_dest, journal_id, qty, description, svl_id, cost))

        if self.company_id.anglo_saxon_accounting:
            # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
            if self._is_dropshipped():
                if cost > 0:
                    am_vals.append(self.with_company(self.company_id)._prepare_account_move_vals(
                        acc_src, acc_valuation, journal_id, qty, description, svl_id, cost))
                else:
                    cost = -1 * cost
                    am_vals.append(self.with_company(self.company_id)._prepare_account_move_vals(
                        acc_valuation, acc_dest, journal_id, qty, description, svl_id, cost))
            elif self._is_dropshipped_returned():
                if cost > 0 and self.location_dest_id._should_be_valued():
                    am_vals.append(self.with_company(self.company_id)._prepare_account_move_vals(
                        acc_valuation, acc_src, journal_id, qty, description, svl_id, cost))
                elif cost > 0:
                    am_vals.append(self.with_company(self.company_id)._prepare_account_move_vals(
                        acc_dest, acc_valuation, journal_id, qty, description, svl_id, cost))
                else:
                    cost = -1 * cost
                    am_vals.append(self.with_company(self.company_id)._prepare_account_move_vals(
                        acc_valuation, acc_src, journal_id, qty, description, svl_id, cost))

        return am_vals

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
                                   cost,
                                   acc_subcontract_valuation=False):
        self.ensure_one()
        valuation_partner_id = self._get_partner_id_for_valuation_lines()
        second_credit_account = acc_subcontract_valuation
        move_ids = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, svl_id, description, second_credit_account=second_credit_account)
        svl = self.env['stock.valuation.layer'].browse(svl_id)
        if self.env.context.get('force_period_date'):
            date = self.env.context.get('force_period_date')
        elif svl.account_move_line_id:
            date = svl.account_move_line_id.date
        else:
            date = fields.Date.context_today(self)
        return {
            'journal_id': journal_id,
            'line_ids': move_ids,
            'partner_id': valuation_partner_id,
            'date': date,
            'ref': description,
            'stock_move_id': self.id,
            'stock_valuation_layer_ids': [(6, None, [svl_id])],
            'move_type': 'entry',
            'is_storno': self.env.context.get('is_returned') and self.company_id.account_storno,
            'company_id': self.company_id.id,
        }

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, svl_id, description,second_credit_account=False):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()

        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        debit_value = self.company_id.currency_id.round(cost)
        credit_value = debit_value

        valuation_partner_id = self._get_partner_id_for_valuation_lines()
        res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description, second_credit_account).values()]


        return res

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description, second_credit_account=False):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()

        line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
        }

        svl = self.env['stock.valuation.layer'].browse(svl_id)
        if svl.account_move_line_id.analytic_distribution:
            line_vals['analytic_distribution'] = svl.account_move_line_id.analytic_distribution

        rslt = {
            'credit_line_vals': {
                **line_vals,
                'balance': -credit_value,
                'account_id': credit_account_id,
            },
            'debit_line_vals': {
                **line_vals,
                'balance': debit_value,
                'account_id': debit_account_id,
            },
        }
        _logger.info(f"normal journal lines  :{rslt}")

        production_id = self.production_id
        if second_credit_account and production_id:
            extra_cost = self.company_id.currency_id.round(production_id.extra_cost * qty)
            material_cost = credit_value - extra_cost
            credit_line_vals = {
                **line_vals,
                'credit': material_cost if material_cost > 0 else 0,
                'balance': -material_cost,
                'debit': -material_cost if material_cost < 0 else 0,
                'account_id': credit_account_id,
            }
            debit_line_vals = {
                **line_vals,
                'balance': debit_value,
                'account_id': debit_account_id,
            }
            second_credit_line_vals = {
                'name': description,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'balance': -extra_cost,
                'credit': extra_cost if extra_cost > 0 else 0,
                'debit': -extra_cost if extra_cost < 0 else 0,
                'account_id': second_credit_account.id,
            }
            rslt = {
                'debit_line_vals': debit_line_vals,
                'credit_line_vals': credit_line_vals,
                'second_credit_line_vals': second_credit_line_vals,
            }
            _logger.info(f"production journal lines  :{rslt}")
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.env.context.get('price_diff_account')
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'balance': -diff_amount,
                'ref': description,
                'partner_id': partner_id,
                'account_id': price_diff_account.id,
            }
        return rslt

    def _get_src_account(self, accounts_data):
        production_id = self.production_id
        _logger.info(f"src account data  :{production_id.x_studio_sourcing.x_studio_order_type}")
        if production_id and production_id.x_studio_sourcing.x_studio_order_type == "Subcontracting":
            return accounts_data['stock_input'].id
        return super()._get_src_account(accounts_data)

    def _get_accounting_data_for_valuation(self):
        """ Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant. """
        self.ensure_one()
        self = self.with_company(self.company_id)
        production_id = self.production_id
        is_subcontract = production_id and production_id.x_studio_sourcing.x_studio_order_type == "Subcontracting"
        accounts_data = self.product_id.product_tmpl_id.get_product_accounts(is_subcontract=is_subcontract)
        _logger.info(f"accounting data  :{is_subcontract}")
        acc_src = self._get_src_account(accounts_data)
        acc_dest = self._get_dest_account(accounts_data)
        acc_subcontract_valuation = accounts_data.get('stock_subcontract_valuation', False)
        acc_valuation = accounts_data.get('stock_valuation', False)
        if acc_valuation:
            acc_valuation = acc_valuation.id
        if not accounts_data.get('stock_journal', False):
            raise UserError(
                _('You don\'t have any stock journal defined on your product category, check if you have installed a chart of accounts.'))
        if not acc_src:
            raise UserError(
                _('Cannot find a stock input account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (
                    self.product_id.display_name))
        if not acc_dest:
            raise UserError(
                _('Cannot find a stock output account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (
                    self.product_id.display_name))
        if not acc_valuation:
            raise UserError(
                _('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))
        journal_id = accounts_data['stock_journal'].id
        if is_subcontract:
            return journal_id, acc_src, acc_dest, acc_valuation, acc_subcontract_valuation
        return journal_id, acc_src, acc_dest, acc_valuation

    def _get_partner_id_for_valuation_lines(self):
        if self.picking_id:
            return (self.picking_id.partner_id and self.env['res.partner']._find_accounting_partner(
                self.picking_id.partner_id).id) or False
        elif self.production_id and self.production_id.x_studio_sourcing:
            return (self.production_id.x_studio_sourcing.partner_id and self.env[
                'res.partner']._find_accounting_partner(
                self.production_id.x_studio_sourcing.partner_id).id) or False
        elif self.raw_material_production_id and self.raw_material_production_id.x_studio_sourcing:
            return (self.raw_material_production_id.x_studio_sourcing.partner_id and \
                    self.env['res.partner']._find_accounting_partner(
                        self.raw_material_production_id.x_studio_sourcing.partner_id).id) or False

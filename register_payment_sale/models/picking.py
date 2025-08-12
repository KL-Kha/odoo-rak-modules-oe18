# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import split_every



# class GlobalChannel(models.Model):
#     _inherit = 'global.channel.ept'
#
#     if_offline = fields.Boolean('Is Offline')


class Picking(models.Model):
    _inherit = 'stock.picking'

    def _get_finance_warning(self):
        result = """
            <center><p style="color:red; font-size: 25px;">Finance Approval is Pending!</p></center>
            """
        return result

    warning_finance = fields.Html('Warning Finance', default=_get_finance_warning, copy=False)
    x_studio_finance_appoved = fields.Boolean(string='Finance Approved')
    condition_fullfill = fields.Boolean(string='Condition Fullfill', compute='_compute_is_finance_available', store=True)
    is_finance_approval_available = fields.Boolean(string='Is Finance Approval Available?', compute='_compute_is_finance_available', store=True)

    # @api.depends('sale_id.x_studio_type', 'sale_id.global_channel_id', 'sale_id.payment_term_id', 'sale_id.x_studio_finance_appoved', 'state', 'move_line_ids_without_package.product_uom_qty')
    # def _compute_is_finance_available(self):
    #     for rec in self:
            # if rec.sale_id.x_studio_type == 'Normal Order' and rec.sale_id.global_channel_id.if_offline == True and rec.sale_id.payment_term_id.x_studio_delivery_payments_required == True and rec.sale_id.x_studio_finance_appoved == False:
            #     if rec.state not in ['done', 'cancel']:
            #         rec.do_unreserve()
            #     rec.is_finance_approval_available = True
            # else:
            #     rec.is_finance_approval_available = False

    @api.depends('sale_id.x_studio_type', 'sale_id.global_channel_id', 'sale_id.payment_term_id', 'sale_id.x_studio_finance_appoved', 'state', 'move_line_ids_without_package')
    def _compute_is_finance_available(self):
        for rec in self:
            rec.x_studio_finance_appoved = rec.sale_id.x_studio_finance_appoved
            if rec.sale_id.x_studio_type.payment_request_required and rec.sale_id.global_channel_id.if_offline == True and rec.sale_id.payment_term_id.x_studio_delivery_payments_required == True and rec.sale_id.x_studio_finance_appoved == False:
                if rec.state not in ['done', 'cancel']:
                    rec.do_unreserve()
                rec.is_finance_approval_available = True
            else:
                rec.is_finance_approval_available = False

            if rec.sale_id.x_studio_type.payment_request_required and rec.sale_id.global_channel_id.if_offline and rec.sale_id.payment_term_id.x_studio_delivery_payments_required:
                rec.condition_fullfill = True
            else:
                rec.condition_fullfill = False

    def action_assign(self):
        for rec in self:
            if rec.is_finance_approval_available:
                raise ValidationError(_("Finance Approval is pending!"))
        return super(Picking, self).action_assign()


class ProcurementGroup(models.Model):

    _inherit = 'procurement.group'

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        # print("************************************", company_id)
        super(ProcurementGroup, self)._run_scheduler_tasks(use_new_cursor=use_new_cursor, company_id=company_id)

        moves_to_assign = self.env['stock.move'].search([
            ('state', 'in', ['confirmed', 'partially_available']),
            ('product_uom_qty', '!=', 0.0)
        ], limit=None, order='priority desc')
        finance_approval_moves = moves_to_assign.filtered(lambda rec: rec.picking_id.is_finance_approval_available)
        for moves_chunk in split_every(100, finance_approval_moves.ids):
            # for p in self.env['stock.move'].browse(moves_chunk):
            #     print("------Unreserved------", p.picking_id.name, p.picking_id.id)
            self.env['stock.move'].browse(moves_chunk).sudo()._do_unreserve()
            if use_new_cursor:
                self._cr.commit()

        moves_to_assign = moves_to_assign.filtered(lambda rec: not rec.picking_id.is_finance_approval_available)

        for moves_chunk in split_every(100, moves_to_assign.ids):
            # for p in self.env['stock.move'].browse(moves_chunk):
            #     print("Reserved", p.picking_id.name, p.picking_id.id)
            self.env['stock.move'].browse(moves_chunk).sudo()._action_assign()
            if use_new_cursor:
                self._cr.commit()

        # Merge duplicated quants
        self.env['stock.quant']._quant_tasks()
        if use_new_cursor:
            self._cr.commit()

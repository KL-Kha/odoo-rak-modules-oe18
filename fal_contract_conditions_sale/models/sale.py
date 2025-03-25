# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('contract_condition_id')
    def onchange_contract_condition_id(self):
        res = {}
        if self.contract_condition_id:
            self.note = self.contract_condition_id.content

            report_ids = self.contract_condition_id.report_ids
            reports = report_ids.filtered(lambda a: a.model == 'sale.order')
            res['domain'] = {'contract_condition_report_id': [
                ('id', 'in', reports.ids),
            ]}
            return res

    contract_condition_id = fields.Many2one(
        'contract.condition',
        string='Contract Condition'
    )
    contract_condition_report_id = fields.Many2one(
        'ir.actions.report',
        string='Contract Condition Report'
    )

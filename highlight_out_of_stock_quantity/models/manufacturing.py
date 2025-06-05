# -*- coding: utf-8 -*-

from odoo import fields, models, api, _



class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def get_trans_detail(self):
        state_selection = dict(self.env['stock.picking'].fields_get(allfields=['state'])['state']['selection'])
        for rec in self:
            html = '<p>'
            for one_line in rec.picking_ids:
                state_label = state_selection.get(one_line.state, one_line.state)
                html += '<b>' + one_line.name + '</b>: ' + state_label + '<br/>'
            html += '</p>'
            rec.transfer_status = html

    transfer_status = fields.Html(string='Transfer status', compute='get_trans_detail')



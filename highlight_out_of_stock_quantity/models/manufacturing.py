# -*- coding: utf-8 -*-

from odoo import fields, models, api, _



class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def get_trans_detail(self):
        for rec in self:
            html = '<p>'
            for one_line in rec.picking_ids:
                    html += '<b>' + one_line.name + '</b>: ' + str(dict(one_line.fields_get(allfields=['state'])['state']['selection'])[one_line.state]) + '<br/>'
            html += '</p>'
            rec.transfer_status = html

    transfer_status = fields.Html(string='Transfer status', compute='get_trans_detail')



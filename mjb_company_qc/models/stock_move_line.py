# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    def _get_check_values(self, quality_point):
        res = super(StockMoveLine, self)._get_check_values(quality_point)
        if self.company_id:
            res['company_id'] = self.company_id.id
        return res
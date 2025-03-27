# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Stock Move'),
            'template': '/base_import_picking_line/static/import_template.xlsx'
        }]

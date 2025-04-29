# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, models, _


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Purchase Requisition Line'),
            'template': '/base_import_purchase_requisition_line/static/import_template.xlsx'
        }]

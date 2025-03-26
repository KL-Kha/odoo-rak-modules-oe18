# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fal_title = fields.Char("Title")

    # this function is from fal_purchase_downwpayment to passing the data. no need to depends the module
    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['fal_title'] = self.fal_title
        return res

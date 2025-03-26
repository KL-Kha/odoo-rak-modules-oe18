# -*- coding: utf-8 -*-
from odoo import fields, models, api
import datetime

class account_invoice(models.Model):
    _inherit = 'account.move'

    fal_title = fields.Char("Title", tracking=True)

    def _get_report_base_filename(self):
        res = super(account_invoice, self)._get_report_base_filename()
        if self.fal_title:
            res = res + ' - ' + self.fal_title
        return res

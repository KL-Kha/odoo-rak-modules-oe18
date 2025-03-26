# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fal_date_start = fields.Date(string='Start Date')
    fal_date_end = fields.Date(string='End Date')

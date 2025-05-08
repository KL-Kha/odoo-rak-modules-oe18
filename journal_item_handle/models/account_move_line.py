# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class NewHandal(models.Model):
    _inherit = "account.move.line"

    sequence_jornal_item = fields.Integer(string='Sequence', default=10)

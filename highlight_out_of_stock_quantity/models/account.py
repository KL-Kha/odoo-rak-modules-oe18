# -*- coding: utf-8 -*-

from odoo import fields, models, api, _



class AccountMove(models.Model):
    _inherit = "account.move"

    please_specify = fields.Char(string="Please Specify")
    responsible_id = fields.Many2one("res.users", string="Responsible")

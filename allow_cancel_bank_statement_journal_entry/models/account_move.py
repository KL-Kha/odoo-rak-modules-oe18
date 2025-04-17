# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, _

class AccountMove(models.Model):
    _inherit = "account.move"

    def _synchronize_business_models(self, changed_fields):
        ''' 
        Original function: File path: odoo/addons/account/models/account_move.py - Method Name: _synchronize_business_models - Line: around 1970
        Only difference is comment out last line
        '''
        return
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def reverse_moves(self):
        # OVERRIDE
        res = super(AccountMoveReversal, self).reverse_moves()
        reverse_move = self.env['account.move'].browse(res['res_id'])
        if self.please_specify:
            reverse_move.please_specify = self.please_specify
        if self.responsible_id:
            reverse_move.responsible_id = self.responsible_id.sudo().id

        return res


    please_specify = fields.Char(string="Please Specify")
    responsible_id = fields.Many2one("res.users", string="Responsible")
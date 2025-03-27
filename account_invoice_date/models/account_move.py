from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def default_get(self, field):
        res = super(AccountMove, self).default_get(field)
        res['invoice_date'] = fields.Date.today()
        return res

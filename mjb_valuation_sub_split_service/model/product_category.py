from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    subcontracted_valuation_account_id = fields.Many2one('account.account', string="SubContract Valuation Account")
    subcontracted_material_account_id = fields.Many2one('account.account', string="SubContract Material Account")

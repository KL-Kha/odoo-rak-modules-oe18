from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    fal_hscode_cat = fields.Char(
        string="HS Code",
        help="Standardized code for international\
        shipping and goods declaration")

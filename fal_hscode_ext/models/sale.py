from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id')
    def compute_hscode(self):
        for rec in self:
            if rec.product_id.hs_code:
                rec.fal_hscode = rec.product_id.hs_code
            else:
                current_categ_id = rec.product_id.categ_id
                while not current_categ_id.fal_hscode_cat and current_categ_id.parent_id:
                    current_categ_id = current_categ_id.parent_id
                rec.fal_hscode = current_categ_id.fal_hscode_cat or False

    fal_hscode = fields.Char(
        string="HS Code",
        compute='compute_hscode', store=True,
        help="Standardized code for international\
        shipping and goods declaration")

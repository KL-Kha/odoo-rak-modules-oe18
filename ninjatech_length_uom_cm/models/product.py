

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = 'product.product'


    @api.model
    def default_get(self, default_vals):
        res = super().default_get(default_vals)
        uom_cm_rec = self.env.ref("uom.product_uom_cm").id
        res.update({
            "fal_length_uom_id": uom_cm_rec,
            "fal_width_uom_id": uom_cm_rec,
            "fal_height_uom_id": uom_cm_rec
        })
        return res


class ProductTemplate(models.Model):

    _inherit = 'product.template'


    @api.model
    def default_get(self, default_vals):
        res = super().default_get(default_vals)
        uom_cm_rec = self.env.ref("uom.product_uom_cm").id
        res.update({
            "fal_length_uom_id": uom_cm_rec,
            "fal_width_uom_id": uom_cm_rec,
            "fal_height_uom_id": uom_cm_rec
        })
        return res

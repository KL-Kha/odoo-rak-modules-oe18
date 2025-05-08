# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#     _sql_constraints = [
#         ('unique_product_barcode', 'unique(barcode)', 'Product Barcode Must Be Unique.'),
#     ]


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    barcode = fields.Char(string='Barcode', related='product_id.barcode')

    # _sql_constraints = [('bom_product_uniq', 'unique (bom_id,product_id)',
    #                      'Duplicate products in BOM Line not allowed !')]

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id and not self.product_id.barcode:
            raise UserError(_('Please add barcode in %s.') % (self.product_id.display_name))
    #     rec = self.bom_id
    #     prds = []
    #     print ('---------',rec.bom_line_ids)
    #     for one_bom_line in rec.bom_line_ids:
    #         prds.append(one_bom_line.product_id)
    #         if not one_bom_line.product_id.barcode:
    #             raise UserError(_('Please add barcode in %s.') % (one_bom_line.product_id.display_name))
    #     print ('-----prds-----',prds)
    #     for one_prd in prds:
    #         if prds.count(one_prd) > 1:
    #             raise UserError(_('You selected %s %s times\n Please select it onetime!') % (
    #             one_prd.display_name, str(prds.count(one_prd))))
        # product = self.product_id
        # title = False
        # message = False
        # result = {}
        # warning = {}
        # title = _("Warning for %s"%(product.name))
        # message = 'aaaaaaaaaaaaa'
        # warning['title'] = title
        # warning['message'] = message
        # result = {'warning': warning}
        # return result

    # @api.model
    # def create(self, vals):
    #     res = super(MrpBomLine, self).create(vals)
    #     res.bom_id.check_uniq_vals()
    #     return res
    #
    # def write(self, vals):
    #     res = super(MrpBomLine, self).write(vals)
    #     for rec in self:
    #         rec.bom_id.check_uniq_vals()
    #     return res

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def check_uniq_vals(self):
        for rec in self:
            prds = []
            for one_bom_line in rec.bom_line_ids:
                prds.append(one_bom_line.product_id)
                if not one_bom_line.barcode:
                    raise UserError(_('Please add barcode in %s.') % (one_bom_line.product_id.display_name))
            for one_prd in prds:
                if prds.count(one_prd) > 1:
                    raise UserError(_('You selected %s %s times\n Please select it onetime!')%(one_prd.display_name, str(prds.count(one_prd))))

    @api.model
    def create(self, vals):
        res = super(MrpBom, self).create(vals)
        res.check_uniq_vals()
        return res

    def write(self, vals):
        res = super(MrpBom, self).write(vals)
        for rec in self:
            rec.check_uniq_vals()
        return res





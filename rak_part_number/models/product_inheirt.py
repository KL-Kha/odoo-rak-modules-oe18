from odoo import api, fields, models, tools
from datetime import datetime


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    def _default_user_ids(self):
        # print('-----------------', self)
        user_ids = self._context.get('active_model') == 'res.users' and self._context.get('active_ids') or []
        # print('---user_ids--------')
        return user_ids
    manufacturer_tmpl_ids = fields.One2many('manufacturer', 'product_tmpl_id', string='Manufacturer')
    tracing = fields.Many2many('purchase.order.line', string='Tracking')


class ProductInherit(models.Model):
    _inherit ='product.product'

    @api.model
    def _get_default_get(self):
        get_manufacturer = self.env['manufacturer'].search([('product_id', '=', self.id)])
        # print('======>>>>', get_manufacturer)
        return get_manufacturer

    manufacturer_prod_ids = fields.One2many('manufacturer', 'product_id', string='Manufacturer')
    tracing = fields.Many2many('purchase.order.line', string='Tracking')
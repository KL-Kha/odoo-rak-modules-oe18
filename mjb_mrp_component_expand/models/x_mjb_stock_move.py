from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    x_parent_product = fields.Char(string='Parent Products', readonly=True)


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    x_expand_component_flag = fields.Boolean(string='Expand Flag', default=False)

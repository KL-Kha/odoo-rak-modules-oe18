# -*- coding: utf-8 -*-
# Import the libraries from Odoo which we need (dependencies)
from odoo import api, fields, models, _

# Define the class we want to override
class MrpProduction(models.Model):
    # Need to provide the model name we want to inherit from, in this case a mrp.bom = a BOM
    _inherit = 'mrp.production'
    
    @api.onchange('product_id', 'move_raw_ids', 'never_product_template_attribute_value_ids')
    def _onchange_product_id(self):
        # for move in self.move_raw_ids:
        #     if self.product_id == move.product_id:
        #         message = _("The component %s should not be the same as the product to produce.", self.product_id.display_name)
        #         self.move_raw_ids = self.move_raw_ids - move
        #         return {'warning': {'title': _('Warning'), 'message': message}}
        return


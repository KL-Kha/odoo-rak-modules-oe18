# -*- coding: utf-8 -*-
# Import the libraries from Odoo which we need (dependencies)
from odoo import api, fields, models, _

# Define the class we want to override
class PurchaseRequisition(models.Model):
    # Need to provide the model name we want to inherit from
    _inherit = 'purchase.requisition'
    
    # Copy paste the base code of the method you want to override, in our case it is the code from here
    
    def action_confirm(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("You cannot confirm agreement '%(agreement)s' because it does not contain any product lines.", agreement=self.name))
        if self.requisition_type == 'blanket_order':
            for requisition_line in self.line_ids:
                # if requisition_line.price_unit <= 0.0:
                #     raise UserError(_('You cannot confirm a blanket order with lines missing a price.'))
                if requisition_line.product_qty <= 0.0:
                    raise UserError(_('You cannot confirm a blanket order with lines missing a quantity.'))
                requisition_line._create_supplier_info()
        self.state = 'confirmed'
        # Set the sequence number regarding the requisition type
        # if self.name == 'New':
        #     if self.is_quantity_copy != 'none':
        #         self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.tender')
        #     else:
        #         self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.blanket.order')

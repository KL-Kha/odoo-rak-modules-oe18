from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    quotation_number = fields.Char(
        'Quotation Number', size=64,
        readonly=True, index=True, copy=False
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_company(vals['company_id']).next_by_code('fal.purchase.quotation.number') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('fal.purchase.quotation.number') or _('New')
        res = super(PurchaseOrder, self).create(vals)
        return res

    def button_confirm(self):
        for purchase_id in self:
            if not purchase_id.quotation_number:
                order_number = purchase_id.name
                if purchase_id.company_id:
                    order_number = self.env['ir.sequence'].with_company(purchase_id.company_id.id).next_by_code('purchase.order') or _('New')
                else:
                    order_number = self.env['ir.sequence'].next_by_code('purchase.order') or _('New')
                purchase_id.write({
                    'name': order_number,
                    'quotation_number': purchase_id.name
                })
        return super(PurchaseOrder, self).button_confirm()

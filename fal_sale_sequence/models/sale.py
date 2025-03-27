from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quotation_number = fields.Char(
        'Quotation Number', size=64,
        readonly=True, index=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_company(vals['company_id']).next_by_code('fal.sale.quotation.number') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('fal.sale.quotation.number') or _('New')
        res = super(SaleOrder, self).create(vals)
        return res

    def action_confirm(self, ):
        for sale_id in self:
            if not sale_id.quotation_number:
                order_number = sale_id.name
                if sale_id.company_id:
                    order_number = self.env['ir.sequence'].with_company(sale_id.company_id.id).next_by_code('sale.order') or _('New')
                else:
                    order_number = self.env['ir.sequence'].next_by_code('sale.order') or _('New')
                sale_id.write({
                    'name': order_number,
                    'quotation_number': sale_id.name
                })
        return super(SaleOrder, self).action_confirm()

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        fields_obj = self.env['ir.model.fields']
        model_obj = self.env['ir.model']
        move_move = model_obj.search([('model', '=', 'account.move')])
        fal_quotation_number = fields_obj.search([('model_id', '=', move_move.id), ('name', '=', 'fal_quotation_number')])
        final_quotation_number = fields_obj.search([('model_id', '=', move_move.id), ('name', '=', 'final_quotation_number')])
        if fal_quotation_number:
            res['fal_quotation_number'] = self.quotation_number
        if final_quotation_number:
            res['final_quotation_number'] = self.quotation_number or self.name
        return res

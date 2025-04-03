from odoo import api, fields, models, _
from datetime import datetime


class Manufacturers(models.Model):
    _name = 'manufacturers'
    _rec_name = 'name'

    name = fields.Char(string='Name')


class Manufacturer(models.Model):
    _name = 'manufacturer'
    _rec_name = 'vid'

    def _compute_po_line_count(self):
        for rec in self:
            get_po = self.env['tracing.popa'].search([('manufacturer_id', '=', rec.id)])
            rec.manufacturer_purchase_order_line_count = len(get_po)

    def default_get(self, fields):
        context = self._context
        res = super(Manufacturer, self).default_get(fields)
        if context.get('default_prod') == True:
            get_product_tmp = self.env['product.product'].search([('id', '=', context.get('default_product_id'))], limit=1)
            res['product_tmpl_id'] = get_product_tmp.product_tmpl_id.id
            res['product_id'] = get_product_tmp
            res['barcode'] = get_product_tmp.barcode
        elif context.get('default_tmpl') == True:
            get_product_tmp = self.env['product.product'].search([('product_tmpl_id', '=', context.get('default_product_tmpl_id'))], limit=1)
            res['product_tmpl_id'] = context.get('default_product_tmpl_id')
            res['product_id'] = get_product_tmp.id
            res['barcode'] = get_product_tmp.barcode
        return res

    vid = fields.Char(string='VID')
    part_number = fields.Char(string='Part Number')
    manufacturer = fields.Many2one('manufacturers', string='Manufacturer')
    active = fields.Boolean(string='Active', default=True)
    start_date = fields.Date(string='Start Date', default=datetime.today())
    end_date = fields.Date(string='End Date')
    product_id = fields.Many2one('product.product', string='Product')
    product_tmpl_id = fields.Many2one('product.template', string='Product')
    barcode = fields.Char(string='Product Barcode')

    tracing = fields.Many2many('purchase.order.line', 'manufacturer_id', string='Tracking')
    manufacturer_purchase_order_line_count = fields.Char(string='Count', compute=_compute_po_line_count)

    # @api.onchange('product_id')
    # def get_tmpl_bar(self):
    #     self.barcode = self.product_id.barcode
    #     self.product_tmpl_id = self.product_id.product_tmpl_id

    def action_view_mf(self):
        # print('-----self0', self)
        action = self.env["ir.actions.actions"]._for_xml_id("rak_part_number.action_tracing_popa")
        action['domain'] = [('manufacturer_id', 'in', self.ids)]
        # print('--action-->>>>>>>>\n\n\n', action)
        return action

    @api.model
    def create(self, vals):
        res = super(Manufacturer, self).create(vals)
        if not res.product_id:
            # print('----if not product_id---\n\n\n', res.product_id)
            search_product_id = self.env['product.product'].search([('product_tmpl_id', '=', res.product_tmpl_id.id)], limit=1)
            res['product_id'] = search_product_id.id
            res['barcode'] = search_product_id.barcode
        elif not res.product_tmpl_id:
            # print('-----------res.product_tmpl_id---', res.product_tmpl_id)
            search_product_id = self.env['product.product'].search([('id', '=', res.product_id.id)], limit=1)
            # print('---search_product_id----\n\n\n', search_product_id)
            res['product_tmpl_id'] = search_product_id.product_tmpl_id.id
            res['barcode'] = search_product_id.barcode
        return res

class TracingPOAndPA(models.Model):
    _name = 'tracing.popa'

    order_ref = fields.Char(string='Order Reference')
    description = fields.Text(string='Description')
    vendor = fields.Char(string='Vendor')
    product_id = fields.Many2one('product.product', string='Product')
    price_unit = fields.Float(string='Unit Price')
    product_qty = fields.Float(string='Quantity')
    manufacturer_id = fields.Many2one('manufacturer', string='Manufacturer')
    get_op_line = fields.Many2one('purchase.order.line', string='OP Line ID')
    get_pa_line = fields.Many2one('purchase.requisition.line', string='PA Line ID')

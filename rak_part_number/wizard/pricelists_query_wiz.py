from odoo import api, fields, models
from datetime import datetime


class PriceListsQueryWiz(models.TransientModel):
    _name = 'pricelists.query.wiz'

    @api.model
    def get_manufacturer(self):
        context = self._context
        # print('-----contect-\n\n\n\n', context)
        if context and context.get('active_model') == 'purchase.order.line' and context.get('active_id'):
            get_po_line = self.env['purchase.order.line'].search([('id', '=', self._context.get('active_id'))])

            # print('----get_po_line--\n\n', get_po_line.manufacturer_id)
            if get_po_line.manufacturer_id:
                return get_po_line.manufacturer_id
            else:
                pass
        elif context and context.get('active_model') == 'purchase.requisition.line' and context.get('active_id'):
            get_pa_line = self.env['purchase.requisition.line'].search([('id', '=', self._context.get('active_id'))])

            # print('----get_po_line--\n\n', get_pa_line.manufacturer_id)
            if get_pa_line.manufacturer_id:
                return get_pa_line.manufacturer_id
            else:
                pass

    manufacturer_ids = fields.Many2many('manufacturer', string='Manufacturer ids', default=get_manufacturer)
    product_id = fields.Many2one('product.product', string='Product')

    def create_vendor(self):
        # print('--------self------', self)
        context = self._context
        # print('--------',self.manufacturer_ids.sorted(key='write_date', reverse=True)[-1])
        manufacturer_list = []
        if not self.manufacturer_ids:
            if context and context.get('active_model') == 'purchase.order.line' and context.get('active_id'):
                po_line_id = self.env['purchase.order.line'].search([('id', '=', self._context.get('active_id'))])
                get_tracing = self.env['tracing.popa'].search([('get_op_line', '=', po_line_id.id)])
                po_line_id.write({
                    'manufacturer_id': None,
                    'part_no': None,
                })
                get_tracing.unlink()
                # print('-----------', self, po_line_id, get_tracing)
            elif context and context.get('active_model') == 'purchase.requisition.line' and context.get('active_id'):
                pa_line_id = self.env['purchase.requisition.line'].search([('id', '=', self._context.get('active_id'))])
                get_tracing = self.env['tracing.popa'].search([('get_pa_line', '=', pa_line_id.id)])
                pa_line_id.write({
                    'manufacturer_id': None,
                    'part_no': None
                })
                get_tracing.unlink()

        for res in self.manufacturer_ids:
            # print('---self.manufacturer_ids-', res)
            if context and context.get('active_model') == 'purchase.order.line' and context.get('active_id'):
                po_line_id = self.env['purchase.order.line'].search([('id', '=', self._context.get('active_id'))])
                get_tracing = self.env['tracing.popa'].search([('get_op_line', '=', po_line_id.id)])
                # print('-----res----', res, res.id, get_tracing.manufacturer_id.id)
                if res.id != get_tracing.manufacturer_id.id:
                    manufacturer_list.append(res)
                else:
                    pass
            elif context and context.get('active_model') == 'purchase.requisition.line' and context.get('active_id'):
                pa_line_id = self.env['purchase.requisition.line'].search([('id', '=', self._context.get('active_id'))])
                # print('--pa_line_id---', pa_line_id)
                get_tracing = self.env['tracing.popa'].search([('get_pa_line', '=', pa_line_id.id)])
                # print('====get_tracing=======', get_tracing)
                if res.id != get_tracing.manufacturer_id.id:
                    manufacturer_list.append(res)
                else:
                    pass

        for rec in manufacturer_list:
            if context and context.get('active_model') == 'purchase.order.line' and context.get('active_id'):
                po_line_id = self.env['purchase.order.line'].search([('id', '=', self._context.get('active_id'))])
                po_line_id.write({'manufacturer_id': rec.id, 'part_no': rec.part_number})
                get_tracing = self.env['tracing.popa'].search([('get_op_line', '=', po_line_id.id)])
                # print('----get_tracing-----', get_tracing)
                if get_tracing:
                    for res in get_tracing:
                        res.unlink()
                    # print('====manufacturer_id>>>>>>>>\n\n\n', po_line_id.manufacturer_id)
                    vals = {
                        'order_ref': po_line_id.order_id.name,
                        'description': po_line_id.product_id.name,
                        'product_id': po_line_id.product_id.id,
                        'manufacturer_id': po_line_id.manufacturer_id.id,
                        'get_op_line': po_line_id.id,
                    }
                    create_tracking = self.env['tracing.popa'].create(vals)

                if not get_tracing:
                    vals = {
                        'order_ref': po_line_id.order_id.name,
                        'description': po_line_id.product_id.name,
                        'product_id': po_line_id.product_id.id,
                        'manufacturer_id': po_line_id.manufacturer_id.id,
                        'get_op_line': po_line_id.id,
                    }
                    create_tracking = self.env['tracing.popa'].create(vals)

            elif context and context.get('active_model') == 'purchase.requisition.line' and context.get('active_id'):
                pa_line_id = self.env['purchase.requisition.line'].search([('id', '=', self._context.get('active_id'))])
                # print('--pa_line_id---', pa_line_id)
                pa_line_id.write({'manufacturer_id': rec.id, 'part_no': rec.part_number})
                get_tracing = self.env['tracing.popa'].search([('get_pa_line', '=', pa_line_id.id)])
                # print('====get_tracing=======', get_tracing)
                if get_tracing:
                    for res in get_tracing:
                        res.unlink()
                    vals = {
                        'order_ref': pa_line_id.requisition_id.name,
                        'description': pa_line_id.product_id.name,
                        'product_id': pa_line_id.product_id.id,
                        'manufacturer_id': pa_line_id.manufacturer_id.id,
                        'get_pa_line': pa_line_id.id,
                    }
                    create_tracking = self.env['tracing.popa'].create(vals)
                if not get_tracing:
                    vals = {
                        'order_ref': pa_line_id.requisition_id.name,
                        'description': pa_line_id.product_id.name,
                        'product_id': pa_line_id.product_id.id,
                        'manufacturer_id': pa_line_id.manufacturer_id.id,
                        'get_pa_line': pa_line_id.id,
                    }
                    create_tracking = self.env['tracing.popa'].create(vals)


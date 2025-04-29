# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class LablePrint(models.TransientModel):
    _name = 'sh.dynamic.lable.print'
    _description = 'Dynamic Lable Print'

    sh_lable_template_id = fields.Many2one(
        'sh.dynamic.template', string="Label Print Template", required=True)
    sh_lable_print_line_ids = fields.One2many(
        'sh.dynamic.lable.print.line', 'lable_id', string='Dynamic Lable Line')
    sh_company_logo = fields.Boolean('Company Logo ?')
    sh_company_logo_height = fields.Char('Logo Height(px)')
    sh_company_logo_width = fields.Char('Logo Width(px)')
    sh_company_logo_align = fields.Selection([('left','Left'),('center','Center'),('right','Right')],string='Logo Align')

    @api.model
    def default_get(self, fields_list):
        res = super(LablePrint, self).default_get(fields_list)
        context = self.env.context
        line_ids = []

        if context.get('active_model') == 'product.template' and context.get('active_ids'):
            for template in self.env[context.get('active_model')].sudo().browse(context.get('active_ids')):
                line_vals = {
                    'product_id': template.product_variant_id.id,
                    'quantity': 1,
                }
                line_ids.append((0, 0, line_vals))
        elif context.get('active_model') == 'product.product' and context.get('active_ids'):
            for product in self.env[context.get('active_model')].sudo().browse(context.get('active_ids')):
                line_vals = {
                    'product_id': product.id,
                    'quantity': 1,
                }
                line_ids.append((0, 0, line_vals))
        elif context.get('active_model') == 'sale.order' and context.get('active_ids'):
            for order in self.env[context.get('active_model')].sudo().browse(context.get('active_ids')):
                for line in order.order_line:
                    line_vals = {
                        'product_id': line.product_id.id,
                        'quantity': int(line.product_uom_qty),
                    }
                    line_ids.append((0, 0, line_vals))
        elif context.get('active_model') == 'account.move' and context.get('active_ids'):
            for move in self.env[context.get('active_model')].sudo().browse(context.get('active_ids')):
                for line in move.invoice_line_ids:
                    line_vals = {
                        'product_id': line.product_id.id,
                        'quantity': int(line.quantity),
                    }
                    line_ids.append((0, 0, line_vals))
        elif context.get('active_model') == 'purchase.order' and context.get('active_ids'):
            for order in self.env[context.get('active_model')].sudo().browse(context.get('active_ids')):
                for line in order.order_line:
                    line_vals = {
                        'product_id': line.product_id.id,
                        'quantity': int(line.product_qty),
                    }
                    line_ids.append((0, 0, line_vals))
        elif context.get('active_model') == 'stock.picking' and context.get('active_ids'):
            for order in self.env[context.get('active_model')].sudo().browse(context.get('active_ids')):
                for line in order.move_ids_without_package:
                    line_vals = {
                        'product_id': line.product_id.id,
                        'quantity': int(line.product_uom_qty),
                    }
                    line_ids.append((0, 0, line_vals))
        res.update({
            'sh_lable_print_line_ids': line_ids
        })
        return res

    def print_dynamic_label(self):
        datas = self.read()[0]
        products = []
        if self.sh_lable_print_line_ids:
            for line in self.sh_lable_print_line_ids:
                product_vals = {
                    'product_id': line.product_id.id,
                    'qty': line.quantity,
                }
                products.append(product_vals)
        datas.update({
            'product_dic': products
        })
        datas.update({
            'sh_lable_template_id': self.sh_lable_template_id.id,
        })
        report_id = self.env.ref(
            'sh_all_in_one_barcode_label.sh_barcode_report_action')
        report_id.sudo().paperformat_id = False
        report_id.sudo().paperformat_id = self.sh_lable_template_id.paperformat_id.id
        return self.env.ref('sh_all_in_one_barcode_label.sh_barcode_report_action').report_action([], data=datas)


class LablePrintLine(models.TransientModel):
    _name = 'sh.dynamic.lable.print.line'
    _description = 'Dynamic Lable Print Line'

    lable_id = fields.Many2one(
        'sh.dynamic.lable.print', string='Dynamic Label')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Integer('Barcode Quantity', default=1)

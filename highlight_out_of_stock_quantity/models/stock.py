# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockMove(models.Model):
    _inherit = "stock.move"
    _order = 'red_line_display desc,difference_qty asc, id desc'

    # product_qty1 = fields.Float('Real Quantity')
    plus_minus_symbol = fields.Char(compute='_compute_plus_minus_symbol', string='', readonly=True)

    @api.depends('availability', 'product_uom_qty')
    def _compute_difference_qty(self):
        print('----self \n\n\n\n', self)
        for rec in self:
            if rec.picking_type_id.show_hl_stock_diff:
                print('-----if inside---')
                red_line = False
                rec.difference_qty = rec.product_uom_qty - rec.availability   # V15 it uses reserved_availability
                if rec.availability < rec.product_uom_qty:
                    red_line = True
                rec.red_line_display = red_line

    difference_qty = fields.Float('Difference', compute='_compute_difference_qty', store=True)
    red_line_display = fields.Boolean('', compute='_compute_difference_qty', store=True)

    def _compute_plus_minus_symbol(self):
        print('------_compute_plus_minus_symbol--\n\n\n', self)
        for rec in self:
            plus_minus_symbol = ''
            if rec.picking_id and rec.picking_id.picking_type_code and rec.picking_id.picking_type_code == 'incoming':
                plus_minus_symbol = '+'
            elif rec.picking_id and rec.picking_id.picking_type_code and rec.picking_id.picking_type_code in [
                'outgoing', 'mrp_operation']:
                plus_minus_symbol = '-'
            elif rec.location_dest_id and rec.location_dest_id.usage in ['internal']:
                plus_minus_symbol = '+'
            elif rec.location_dest_id and rec.location_dest_id.usage in ['inventor', 'production']:
                plus_minus_symbol = '-'
            rec.plus_minus_symbol = plus_minus_symbol


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    _order = 'difference_qty asc, id desc'

    plus_minus_symbol = fields.Char(compute='_compute_plus_minus_symbol', string='', readonly=True)
    difference_qty = fields.Float('Difference', related='move_id.difference_qty', store=True)

    def _compute_plus_minus_symbol(self):
        for rec in self:
            plus_minus_symbol = ''
            if rec.move_id and rec.move_id.picking_id and rec.move_id.picking_id.picking_type_code and rec.move_id.picking_id.picking_type_code == 'incoming':
                plus_minus_symbol = '+'
            elif rec.move_id and rec.move_id.picking_id and rec.move_id.picking_id.picking_type_code and rec.move_id.picking_id.picking_type_code in [
                'outgoing', 'mrp_operation']:
                plus_minus_symbol = '-'
            elif rec.move_id.location_dest_id and rec.move_id.location_dest_id.usage in ['internal']:
                plus_minus_symbol = '+'
            elif rec.move_id.location_dest_id and rec.move_id.location_dest_id.usage in ['inventor', 'production']:
                plus_minus_symbol = '-'
            rec.plus_minus_symbol = plus_minus_symbol


class StockPickingTypeInherit(models.Model):
    _inherit = 'stock.picking.type'

    show_hl_stock_diff = fields.Boolean(string='Show Highlighted Stock Difference')


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    related_show_hl_stock_diff = fields.Boolean(string='Rel Highlighted Stock Difference',
                                                related='picking_type_id.show_hl_stock_diff')

    hl_active = fields.Boolean(compute='_compute_ht_active_', string='HL Active')

    def _compute_ht_active_(self):
        for rec in self:
            count = []
            for mv in rec.move_ids_without_package:
                if mv.red_line_display:
                    count.append(mv.id)
            if len(count) > 0:
                rec.hl_active = True
            else:
                rec.hl_active = False


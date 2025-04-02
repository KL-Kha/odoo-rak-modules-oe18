from odoo import fields, models
import logging

logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"

    def sale_sorting_order(self, item):
        # print("self........", self, item)
        # default_field = item.picking_id.create_date.date()
        current_date = fields.Date.today()
        default_field = item.picking_id.create_date and item.picking_id.create_date.date()
        delivery_date = item.picking_id.x_studio_required_delivery_datecrd
        schedule_date = item.picking_id.x_studio_schedule_date_csd and item.picking_id.x_studio_schedule_date_csd.date()

        if delivery_date:
            required_delivery_diff = (delivery_date - current_date).days
        else:
            required_delivery_diff = float('inf')

        if schedule_date:
            schedule_diff = (schedule_date - current_date).days
        else:
            schedule_diff = float('inf')
        if default_field:
            create_date_diff = (default_field - current_date).days
        else:
            create_date_diff = float('inf')
        logger.info("item......... origin={}, min_diff={}".format(item.origin, min(required_delivery_diff, schedule_diff, create_date_diff)))
        if required_delivery_diff or required_delivery_diff == 0:
            return required_delivery_diff
        elif schedule_diff or schedule_diff == 0:
            return schedule_diff
        elif create_date_diff or create_date_diff == 0:
            return create_date_diff
        else:
            return float('inf')

    def mo_sorting_order(self, item):
        current_date = fields.Date.today()
        default_field = item.picking_id.create_date and item.picking_id.create_date.date()
        date_deadline = item.picking_id.date_deadline and item.picking_id.date_deadline.date()
        schedule_date = item.picking_id.scheduled_date and item.picking_id.scheduled_date.date()
        # default_field = item.picking_id.create_date
        # return default_field
        if date_deadline:
            date_delivery_diff = (date_deadline - current_date).days
        else:
            date_delivery_diff = float('inf')
        if schedule_date:
            schedule_date_diff = (schedule_date - current_date).days
        else:
            schedule_date_diff = float('inf')
        if default_field:
            create_date_diff = (default_field - current_date).days
        else:
            create_date_diff = float('inf')
        if date_delivery_diff or date_delivery_diff == 0:
            return date_delivery_diff
        elif schedule_date_diff or schedule_date_diff == 0:
            return schedule_date_diff
        elif create_date_diff or create_date_diff == 0:
            return create_date_diff
        else:
            return float('inf')

    def _action_assign(self):
        # res = super()._action_assign()
        wh_location_ids = self.wh_locations()
        out_domain = self._move_out_domain(product_variant_ids=self.mapped('product_id.id'),
                                           wh_location_ids=wh_location_ids)
        out_moves = self.search(out_domain)
        logger.info(f"out_moves: {out_moves}, out_domain: {out_domain}")
        extra_moves = self
        total_qty = 0
        for move in self:
            forced_package_id = move.package_level_id.package_id or None
            total_qty += move.product_qty
            if total_qty >= move._get_available_quantity(move.location_id, package_id=forced_package_id):
                # filtered_moves = out_moves.filtered(lambda m: m.state == 'assigned')
                production_move = out_moves.filtered(
                    lambda m: m.raw_material_production_id or m.production_id)
                other_move = out_moves
                logger.info(f"production: {production_move}")

                if production_move and move in production_move:
                    production_move = production_move.sorted(
                        self.mo_sorting_order, reverse=True)
                    logger.info(f"production: {production_move}")
                    move_index = list(production_move).index(move)
                    if move_index + 2 <= len(production_move):
                        production_move = production_move[move_index + 1:].filtered(
                            lambda pm: pm.state in ['assigned', 'partially_available'])
                        qty_need = move.product_qty
                        if production_move:
                            qty_reserved = 0
                            index = 0
                            while qty_reserved <= qty_need and index < len(production_move):
                                qty_reserved += production_move[index].product_qty
                                production_move[index]._do_unreserve()
                                extra_moves |= production_move[index]
                                index += 1

                elif other_move and move in other_move:
                    filtered_moves = other_move.sorted(self.sale_sorting_order)
                    logger.info(f"filtered_moves (origin): {filtered_moves.mapped('origin')}")
                    move_index = list(filtered_moves).index(move)
                    # if move_index + 2 <= len(filtered_moves):
                    filtered_moves = filtered_moves.filtered(
                        lambda pm: pm.state in ['assigned', 'partially_available'])
                    qty_need = move.product_qty
                    # reserved_qty = sum([flmv.reserved_availability or flmv.product_qty \
                    #                     for flmv in filtered_moves])
                    # reserved_qty = sum(filtered_moves.mapped('reserved_availability'))

                    if filtered_moves:
                        qty_reserved = 0
                        index = move_index
                        while qty_reserved <= qty_need and index < len(filtered_moves):
                            qty_reserved += filtered_moves[index].product_qty
                            filtered_moves[index]._do_unreserve()
                            extra_moves |= filtered_moves[index]
                            index += 1
        super(StockMove, extra_moves or self)._action_assign()
        # return res

        #
        # for move in self.filtered(lambda m: m.state in ['confirmed', 'waiting', 'partially_available']):
        #     forced_package_id = move.package_level_id.package_id or None
        #     if move.product_qty <= move._get_available_quantity(move.location_id, package_id=forced_package_id):
        #         res = super()._action_assign()
        #         return res
        #     else:
        #         reserved_move = out_moves - move
        #         reserved_move._do_unreserve()

    def _product_domain(self, product_template_ids=False, product_variant_ids=False):
        if product_template_ids:
            return [('product_tmpl_id', 'in', product_template_ids)]
        return [('product_id', 'in', product_variant_ids)]

    def _move_out_domain(self, product_template_ids=False, product_variant_ids=False, wh_location_ids=[]):
        move_domain = self._product_domain(product_template_ids, product_variant_ids)
        move_domain += [('product_uom_qty', '!=', 0)]
        out_domain = move_domain + [
            '&',
            ('location_id', 'in', wh_location_ids),
            ('location_dest_id', 'not in', wh_location_ids),
        ]

        return out_domain

    def wh_locations(self):
        if self.env.context.get('warehouse'):
            warehouse = self.env['stock.warehouse'].browse(self.env.context.get('warehouse'))
        else:
            # warehouse = self.env.ref('__export__.stock_warehouse_7_67291a12')
            warehouse = self.env['stock.warehouse'].browse(
                self.env['stock.warehouse'].search_read(fields=['id', 'name', 'code'])[0]['id'])
        wh_location_ids = [loc['id'] for loc in self.env['stock.location'].search_read(
            [('id', 'child_of', warehouse.view_location_id.id), ('usage', '=', 'view')],
            ['id'],
        )]
        logger.info(f"warehouse locations: {wh_location_ids.mapped('name')}")
        return wh_location_ids

# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    battery = fields.Boolean(related='product_id.battery',string="Battery")


class StockMove(models.Model):
    _inherit = "stock.move"

    battery = fields.Boolean(related='product_id.battery',string="Battery")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_battery_info(self):
        for rec in self:
            battery = False
            for one_line in rec.move_line_ids_without_package:
                if one_line.product_id and one_line.product_id.battery:
                    battery = True
            rec.battery = battery

    battery = fields.Boolean(compute='get_battery_info', string="Battery")

    # @api.depends('order_line','order_line.product_id')
    # def get_battery_info(self):
    #     for rec in self:
    #         battery = False
    #         for one_line in rec.order_line:
    #             if one_line.product_id and one_line.product_id.battery:
    #                 battery = True
    #         rec.battery = battery
    #
    # battery = fields.Boolean(compute='get_battery_info', string="Battery", store=True)

# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    battery = fields.Boolean(related='product_id.battery',string="Battery")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_battery_info(self):
        for rec in self:
            battery = False
            for one_line in rec.order_line:
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

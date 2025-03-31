# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from markupsafe import Markup


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def pmc_packing_log_btn(self):
        team = self.env['message.team'].sudo().search([("is_active", "=", True), ("is_pmc_packing_team", "=", True)])[
               :1]
        body = ""
        if team:
            team_members = team.member_ids
            if team_members:
                for team in team_members:
                    body += Markup(_(' <a href=# data-oe-model=res.users data-oe-id=%d>@%s</a> ')) % (team.id, team.name)
                body += Markup(_('<br> 请关注Please note SO：%s')) % (self.name)
                if 'x_studio_delivery_note' in self.env['sale.order']._fields:
                    if self.x_studio_delivery_note:
                        body += Markup(_('<br> 订单备注Delivery note：%s')) % (self.x_studio_delivery_note)
                    else:
                        body += Markup(_('<br> 订单备注Delivery note： '))
                if 'x_studio_shipping_notice_id' in self.env['sale.order']._fields:
                    if self.x_studio_shipping_notice_id.x_name:
                        body += Markup(_('<br> 发货须知Shipping notice：%s')) % (self.x_studio_shipping_notice_id.x_name)
                    else:
                        body += Markup(_('<br> 发货须知Shipping notice： '))
                if 'x_studio_package_notice_id' in self.env['sale.order']._fields:
                    if self.x_studio_package_notice_id.x_name:
                        body += Markup(_('<br> 包装要求Package notice: %s')) % (self.x_studio_package_notice_id.x_name)
                    else:
                        body += Markup(_('<br> 包装要求Package notice: '))
                self.message_post(body=body, partner_ids=team_members.partner_id.ids)

    def logistics_log_btn(self):
        team = self.env['message.team'].sudo().search([("is_active", "=", True), ("is_logistics_team", "=", True)])[:1]
        body = ""
        if team:
            team_members = team.member_ids
            if team_members:
                for team in team_members:
                    body += Markup(_(' <a href=# data-oe-model=res.users data-oe-id=%d>@%s</a> ')) % (team.id, team.name)
                body += Markup(_('<br> 请关注Please note SO：%s')) % (self.name)
                if 'x_shipping_forwarder_id' in self.env['sale.order']._fields:
                    if self.x_shipping_forwarder_id.x_name:
                        body += Markup(_('<br> 货代Shipping forwarder: %s')) % (self.x_shipping_forwarder_id.x_name)
                    else:
                        body += Markup(_('<br> 货代Shipping forwarder: '))
                if 'x_studio_shipping_carrier' in self.env['sale.order']._fields:
                    if self.x_studio_shipping_carrier.x_name:
                        body += Markup(_('<br> 承运商Shipping carrier: %s')) % (self.x_studio_shipping_carrier.x_name)
                    else:
                        body += Markup(_('<br> 承运商Shipping carrier: '))
                self.message_post(body=body, partner_ids=team_members.partner_id.ids)

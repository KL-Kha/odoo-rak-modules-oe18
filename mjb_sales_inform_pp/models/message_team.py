# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MessageTeam(models.Model):
    _name = 'message.team'
    _description = 'Message Team'
    _rec_name = 'team_name'

    team_name = fields.Char("Name", required=True)
    is_active = fields.Boolean("Active", default=False)
    is_pmc_packing_team = fields.Boolean("PMC/Packing Team", default=False)
    is_logistics_team = fields.Boolean("Logistics Team", default=False)
    member_ids = fields.Many2many('res.users', string='Team Members', help="Users assigned to this team.")

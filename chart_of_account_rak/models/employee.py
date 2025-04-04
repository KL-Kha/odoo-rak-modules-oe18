from odoo import api, fields, models, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    partner_id = fields.Many2one('res.partner', string='Related Partner', related='user_id.partner_id', store=True)
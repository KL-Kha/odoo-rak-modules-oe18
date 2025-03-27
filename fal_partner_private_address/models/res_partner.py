from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command

class Partner(models.Model):
    _description = 'Contact'
    _inherit = "res.partner"

    type = fields.Selection(selection_add=[
        ('private', 'Private Address'),
    ], ondelete={'private': 'cascade'})


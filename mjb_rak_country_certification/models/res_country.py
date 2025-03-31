# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools


class ResCountry(models.Model):
    _inherit = 'res.country'

    x_certification_ids = fields.Many2many(
        'x_mjb_certification',
        'country_certification_rel',
        'certification_id',
        'country_id',
        string="Certification"
    )

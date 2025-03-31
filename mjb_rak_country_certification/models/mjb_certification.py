# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools


class MjbCertification(models.Model):
    _name = 'x_mjb_certification'
    _description = 'x_mjb_certification'
    _rec_name = 'x_name'

    x_name = fields.Char(string="Certification")
    x_country_ids = fields.Many2many(
        'res.country',
        'country_certification_rel',
        'country_id',
        'certification_id',
        string="Country"
    )

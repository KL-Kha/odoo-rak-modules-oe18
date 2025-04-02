# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        readonly=True,
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('type', 'in', ['normal', 'subcontract'])]""",
        check_company=True,
        help="Bill of Materials allow you to define the list of required components to make a finished product.")

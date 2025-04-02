from odoo import fields, models


class QualityPoint(models.Model):
    _inherit = "quality.point"

    quality_tag_ids = fields.Many2many('quality.tag')



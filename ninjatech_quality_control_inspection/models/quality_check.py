from odoo import api, models, fields


class QualityChecks(models.Model):
    _inherit = "quality.check"

    @api.depends('point_id')
    def _onchange_control_point(self):
        for rec in self:
            if rec.quality_state not in ['pass', 'fail'] and rec.point_id:
                quality_check_ids = []
                if rec.quality_check_ids:
                    rec.quality_check_ids = [(5, 0)]
                for tag in rec.point_id.quality_tag_ids:
                    quality_check_ids.append((0, 0, {
                        "quality_tag_id": tag.id
                    }))
                rec.quality_check_ids = quality_check_ids
            elif rec.quality_state in ['pass', 'fail'] and rec.quality_check_ids:
                rec.quality_check_ids
            else:
                rec.quality_check_ids = [(5, 0)]

    quality_check_ids = fields.One2many('quality.check.tags',
                                        'quality_check_id',
                                        compute="_onchange_control_point",
                                        store=True,
                                        readonly=False
                                        )

    def do_pass(self):
        # self._onchange_control_point()
        res = super().do_pass()
        for rec in self.quality_check_ids:
            rec.quality_check = True
        return res


class QualityCheckTags(models.Model):
    _name = "quality.check.tags"

    quality_tag_id = fields.Many2one('quality.tag')
    quality_check = fields.Boolean("Is Ok?")
    quality_check_id = fields.Many2one("quality.check")
    test_value = fields.Char("Value")
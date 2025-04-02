from odoo import api, fields, models


class QualityCheckWizard(models.TransientModel):
    _inherit = "quality.check.wizard"



    @api.model
    def default_get(self, field_list=None):
        res = super().default_get(field_list)
        quality_check_id = res.get('current_check_id')
        quality_check_rec = quality_check_id and self.env['quality.check'].browse(quality_check_id)
        if quality_check_rec:
            quality_check_ids = []
            for tag in quality_check_rec.point_id.quality_tag_ids:
                quality_check_ids.append((0, 0, {
                    "quality_tag_id": tag.id,
                    "quality_check": True
                }))
            res.update({
                "quality_check_ids": quality_check_ids
            })
        return res

    quality_check_ids = fields.One2many('quality.check.wizard.tags',
                                        'quality_wizard_id')

    def do_measure(self):
        res = super().do_measure()
        quality_tag_line = []
        for rec in self.quality_check_ids:
            quality_tag_line.append((0, 0, {
                "quality_tag_id": rec.quality_tag_id.id,
                "quality_check": rec.quality_check,
                "test_value": rec.test_value
            }))
        self.current_check_id.quality_check_ids = [(5, 0)]
        self.current_check_id.quality_check_ids = quality_tag_line


class QualityCheckWizardTags(models.TransientModel):
    _name = "quality.check.wizard.tags"

    quality_tag_id = fields.Many2one('quality.tag')
    quality_check = fields.Boolean("Is Ok?")
    quality_wizard_id = fields.Many2one('quality.check.wizard')
    test_value = fields.Char("Value")
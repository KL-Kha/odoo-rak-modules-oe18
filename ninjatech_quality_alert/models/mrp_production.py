from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_quality_alert(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "quality_control.quality_alert_action_check")
        action['views'] = [(False, 'form')]
        quantity_checks = sum(self.check_ids.filtered(
            lambda rec: rec.quality_state == 'pass').mapped('qty_tested'))
        action['context'] = {
            'default_company_id': self.company_id.id,
            'default_product_id': self.product_id.id,
            'default_product_tmpl_id': self.product_id.product_tmpl_id.id,
            'default_production_id': self.id,
            "default_x_studio_mo": self.id,
            "default_x_studio_qty_checked": quantity_checks
        }
        return action

class StockPicking(models.Model):

    _inherit = "stock.picking"

    def button_quality_alert(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("quality_control.quality_alert_action_check")
        action['views'] = [(False, 'form')]
        quantity_checks = sum(self.check_ids.filtered(
            lambda rec: rec.quality_state == 'pass').mapped('qty_tested'))
        mrp_production_id = self.env['mrp.production'].search([('name', '=', self.origin)], limit=1)
        action['context'] = {
            'default_product_id': self.product_id.id,
            'default_product_tmpl_id': self.product_id.product_tmpl_id.id,
            'default_picking_id': self.id,
            "default_x_studio_mo": mrp_production_id.id,
            "default_x_studio_qty_checked": quantity_checks
        }
        return action
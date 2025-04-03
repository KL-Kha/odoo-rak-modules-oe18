from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    manufacturer_id = fields.Many2one('manufacturer', string='Manufacturer')
    part_no = fields.Char(string='Part No')
    vid_ref = fields.Many2one('manufacturer', string='VID ref')

    def call_manufacturer_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("rak_part_number.action_manufacturer")
        record_ids = self.env['manufacturer'].search([])
        rec_tree = self.env.ref('rak_part_number.manufacturer_view_tree1').id
        rec_tree1 = self.env.ref('rak_part_number.manufacturer_view_tree1').id
        action['res_ids'] = record_ids.ids,
        action['target'] = 'new'
        action['view_id'] = rec_tree
        action['view_mode'] = 'tree'
        return action


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.requisition.line'

    manufacturer_id = fields.Many2one('manufacturer', string='Manufacturer')
    part_no = fields.Char(string='Part No')
    vid_ref = fields.Many2one('manufacturer', string='VID ref')

    def call_manufacturer_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("rak_part_number.action_manufacturer")
        record_ids = self.env['manufacturer'].search([])
        rec_tree = self.env.ref('rak_part_number.manufacturer_view_tree1').id
        rec_tree1 = self.env.ref('rak_part_number.manufacturer_view_tree1').id
        action['res_ids'] = record_ids.ids,
        action['target'] = 'new'
        action['view_id'] = rec_tree
        action['view_mode'] = 'tree'
        return action
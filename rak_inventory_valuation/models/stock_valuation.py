from odoo import models, fields, api

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    inventory_age = fields.Integer(
        string='Inventory Age (Days)', compute='_compute_inventory_age', store=True)

    @api.depends('create_date')
    def _compute_inventory_age(self):
        for record in self:
            if record.create_date:
                record.inventory_age = (fields.Date.today() - record.create_date.date()).days
            else:
                record.inventory_age = 0

    def compute_inventory_age_totals(self):

        age_totals = {
            '0_30_days': {'quantity': 0.0, 'value': 0.0},
            '30_60_days': {'quantity': 0.0, 'value': 0.0},
            '60_90_days': {'quantity': 0.0, 'value': 0.0},
            'over_90_days': {'quantity': 0.0, 'value': 0.0},
            'over_180_days': {'quantity': 0.0, 'value': 0.0}
        }

        records = self.search([('location_id.usage', '!=', 'internal')])

        for record in records:
            age_days = record.inventory_age
            if age_days <= 30:
                age_totals['0_30_days']['quantity'] += record.quantity
                age_totals['0_30_days']['value'] += record.value
            elif 30 < age_days <= 60:
                age_totals['30_60_days']['quantity'] += record.quantity
                age_totals['30_60_days']['value'] += record.value
            elif 60 < age_days <= 90:
                age_totals['60_90_days']['quantity'] += record.quantity
                age_totals['60_90_days']['value'] += record.value
            elif 90 < age_days <= 180:
                age_totals['over_90_days']['quantity'] += record.quantity
                age_totals['over_90_days']['value'] += record.value
            else:
                age_totals['over_180_days']['quantity'] += record.quantity
                age_totals['over_180_days']['value'] += record.value

        return age_totals
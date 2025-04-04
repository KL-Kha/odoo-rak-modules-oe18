from odoo import api, fields, models, SUPERUSER_ID, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        return super(SaleOrder, self)._create_invoices(grouped=True, final=final, date=date)
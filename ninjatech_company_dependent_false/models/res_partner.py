

from odoo import  fields, models

class ResPartner(models.Model):

    _inherit = "res.partner"

    property_payment_term_id = fields.Many2one('account.payment.term',company_dependent=False,
                                               string='Customer Payment Terms',
                                               domain="[('company_id', 'in', [current_company_id, False])]",
                                               help="This payment term will be used instead of the default one for sales orders and customer invoices")
    property_supplier_payment_term_id = fields.Many2one('account.payment.term', company_dependent=False,
                                                        string='Vendor Payment Terms',
                                                        domain="[('company_id', 'in', [current_company_id, False])]",
                                                        help="This payment term will be used instead of the default one for purchase orders and vendor bills")
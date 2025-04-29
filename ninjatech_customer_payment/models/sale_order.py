from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        readonly=False
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        pricelist_rec = self.env['product.pricelist'].search(
            [("name", "=", "RAK Wireless Store (Production) PriceList")],
                                    limit=1)
        res.update({
            "pricelist_id": pricelist_rec.id
        })
        return res

    def prepare_shopify_order_vals(self, instance, partner, shipping_address,
                                   invoice_address, order_response, payment_gateway,
                                   workflow):
        order_vals = super().prepare_shopify_order_vals(instance, partner, shipping_address,
                                                        invoice_address, order_response, payment_gateway,
                                                        workflow)
        payment_term_id = self.env.ref("account.account_payment_term_immediate").id

        order_vals.update({
            "payment_term_id": payment_term_id
        })
        return order_vals

    @api.onchange("partner_id")
    def onchange_customer(self):
        for rec in self:
            rec.payment_term_id = rec.partner_id.property_payment_term_id.id

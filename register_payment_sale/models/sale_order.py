from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
import logging
import json
import time
import decimal
import requests
# import tenacity

_logger = logging.getLogger(__name__)


class GlobalChannel(models.Model):
    _name = 'global.channel.ept'
    _description = 'Global Channel'

    name = fields.Char('Global Channel')
    if_offline = fields.Boolean('Payment Request Required')


class SaleOrderType(models.Model):
    _name = "sale.type"
    name = fields.Char('Type')
    payment_request_required = fields.Boolean('Payment Request Required?')


class ShopifyParserForCarrierServiceRates:
    """
    NOTE: Consider moving to another utility module
    """
    debug = False

    # constructor function
    def __init__(self, debug=False):
        self.debug = debug

    def process(self, customer, destination, line_items):
        # origin = self.parse_origin(customer)
        # if self.debug:
        #     print_with_syntax_highlighting(origin)
    
        destination = self.parse_destination(destination)
        if self.debug:
            print_with_syntax_highlighting(destination)

        line_items = self.parse_line_items(line_items)
        if self.debug:
            print_with_syntax_highlighting(line_items)

        # NOTE used for local integration testing only.
        mocked_destination = {
            "country": "PH",
            "postal_code": "6200",
            "province": "PH-NER",
            "city": "Dumaguete City",
            "name": "Phoenix Eve Aspacio",
            "address1": "548 Fortune Homes Pulantubig",
            "address2": ""
        }

        origin = {
            "address1": "3F, BaiYang Ind.Park, ShiYan Sub-district, Bao'An District",
            "address2": "",
            "city": "Shenzhen",
            "province": "Guangdong",
            "country": "CN",
            "name": "RAKwireless",
            "company_name": "RAKwireless",
            "postal_code": "518108",
        },

        body = {
            'rate': {
                'origin': origin,
                'destination': destination,
                'items': line_items,
                'currency': 'USD'
            }
        }
        _logger.info(f"=> [TRACING] ShopifyParserForCarrierServiceRates POST body={body} / JSON body={json.dumps(body)}")

        uri = "https://cs-api.rakwireless.com/carrier_service_rates.php"
        r = requests.post(uri, headers={"Content-type": "application/json"}, data=json.dumps(body))
        data = r.json()
        _logger.info(f"=> [TRACING] ShopifyParserForCarrierServiceRates POST {uri} -> Resp: {data}")

        # NOTE used to simulate response from CS-API
        # data = {'rates': [
        #     [
        #         {'service_name': 'Global Standard Express (DAP)', 'service_code': 'GSE-DAP', 'total_price': 2561,
        #          'description': 'Delivered At Place, taxes and duties unpaid, shipped via DHL/UPS/FedEx/EMS/Aramex',
        #          'currency': 'USD', 'min_delivery_date': '2024-03-16 04:18:30 +0000',
        #          'max_delivery_date': '2024-03-23 04:18:30 +0000'},
        #         {'service_name': 'CN-US Express Line (DDP)', 'service_code': 'CN-US-DDP', 'total_price': 831,
        #          'description': 'Delivered Duties Paid, shipped via CN-US commercial carriers', 'currency': 'USD',
        #          'min_delivery_date': '2024-03-29 04:18:30 +0000', 'max_delivery_date': '2024-04-06 04:18:30 +0000'}
        #     ]
        # ]}

        try:
            resp = {"rates": data['rates'][0]}
        except IndexError:
            resp = {"rates": []}

        return resp

    def parse_line_items(self, source_data):
        items = []

        for item in source_data:
            if item["sku"] != "shopifyshippingproduct" \
                    and item["sku"] != "shopify_shipping" \
                    and item["price"] != "":
                items.append(
                    {
                        "name": item["name"] or "",
                        "sku": item["sku"] or "",
                        "quantity": item["quantity"] or "",
                        "grams": item["grams"] or "",
                        "price": item["price"] or "",
                        "vendor": item["vendor"] or "",
                        "requires_shipping": item["requires_shipping"] or False,
                        "taxable": item["taxable"] or False,
                        "fulfillment_service": item["fulfillment_service"] or "",
                        "properties": item["properties"] or {},
                        "product_id": item["product_id"] or "",
                        "variant_id": item["variant_id"] or ""
                    }
                )

        return items

    def parse_origin(self, source_data):
        origin = self.filter_by_keys(
            ['province_code', 'first_name', 'last_name', 'county_code'],
            source_data['default_address'])
        origin['email'] = source_data['email']
        # print_with_syntax_highlighting(origin)

        renamed = self.rename_keys({
            'company': 'company_name',
            'zip': 'postal_code'
        }, origin)

        return renamed

    def parse_destination(self, source_data):
        destination = self.filter_by_keys(['province_code', 'first_name', 'last_name', 'county_code'], source_data)
        # print_with_syntax_highlighting(destination)

        renamed = self.rename_keys({
            'company': 'company_name',
            'zip': 'postal_code'
        }, destination)

        return renamed

    def rename_keys(self, list, input):
        for original_key in list:
            input[list[original_key]] = input[original_key]
            input.pop(original_key)

        return input

    def filter_by_keys(self, keys, input):
        output: dict = {}
        filter_data = [x for x in input if all(y not in x for y in keys)]

        for k in filter_data:
            output[k] = input[k] or None

        return output

    def flatten(self, matrix):
        _logger.info(f"=> [TRACING] flatten={matrix}")

        flat_list = []
        for row in matrix:
            flat_list.extend(row)

        return flat_list

def print_with_syntax_highlighting(source):
    """
    Wrapper for printing output from `ShopifyParserForCarrierServiceRates`
    """
    _logger.info(f"=> [TRACING] print_with_syntax_highlighting={source}")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    battery = fields.Boolean("battery")
    advance_account_payment_ids = fields.Many2many('account.payment', string='Advance Payments', copy=False)
    advance_payment_count = fields.Integer('Advance Payment Count', compute='advance_payment', copy=False, store=True)
    total_register_payment = fields.Monetary('Total Registered Amount', compute='_get_total_register_payment',
                                             store=True, copy=False)
    total_request_amount = fields.Monetary('Total Requested Amount', compute='_get_total_register_payment',
                                           store=True, copy=False)
    payment_amount = fields.Monetary('Request Amount', copy=False)
    due_amount = fields.Monetary('Due Amount', compute='_get_total_register_payment', store=True, copy=False)
    x_studio_finance_appoved = fields.Boolean('Finance Approved', tracking=True, copy=False)
    x_studio_delivery_payments_required = fields.Boolean('Is Delivery Payment Required?',
                                                         related='payment_term_id.x_studio_delivery_payments_required')
    x_studio_type = fields.Many2one('sale.type', 'Type')
    payment_request_required = fields.Boolean('Payment Request Required?',
                                              related='x_studio_type.payment_request_required')
    global_channel_id = fields.Many2one('global.channel.ept', string='Global Channel')
    if_offline = fields.Boolean('Is Offline?', related='global_channel_id.if_offline')
    is_any_picking_done = fields.Boolean('Is Any Picking Done', compute='_get_picking_done', store=True)

    @api.depends('picking_ids', 'picking_ids.state')
    def _get_picking_done(self):
        for rec in self:
            if any(rec.picking_ids.filtered(lambda picking: picking.state in ('done'))):
                rec.is_any_picking_done = True
            else:
                rec.is_any_picking_done = False

    def action_cancel_payment_sale_order(self):
        for rec in self:
            for payment in rec.advance_account_payment_ids:
                if payment.state == 'posted':
                    payment.action_cancel()
                if payment.state == 'draft':
                    payment.action_cancel()

    def action_finance_approved(self):
        for rec in self:
            rec.x_studio_finance_appoved = True
            payment_rec = self.env['sale.order.payment'].search([('sale_order_id', '=', rec._origin.id)])
            if payment_rec:
                self.env['mail.message'].create({
                    'body': "Finance Approved -> True " + rec.name,
                    'model': 'account.payment',
                    'res_id': payment_rec[0].payment_id.id,
                })

    def action_finance_reject(self):
        for rec in self:
            rec.x_studio_finance_appoved = False
            payment_rec = self.env['sale.order.payment'].search([('sale_order_id', '=', rec._origin.id)])
            if payment_rec:
                self.env['mail.message'].create({
                    'body': "Finance Approved -> False " + rec.name,
                    'model': 'account.payment',
                    'res_id': payment_rec[0].payment_id.id,
                })

    @api.depends('advance_account_payment_ids', 'advance_account_payment_ids.state',
                 'advance_account_payment_ids.sale_order_ids', 'order_line')
    def _get_total_register_payment(self):
        for rec in self:
            sale_order_payment_ids = self.env['sale.order.payment'].search([('sale_order_id', '=', rec.id)])
            total_register_payment = 0
            total_request_amount = 0
            for payment_order in sale_order_payment_ids:
                if payment_order.payment_id.state in ['posted', 'reconciled']:
                    total_register_payment += payment_order.register_amount
                if payment_order.payment_id.state in ['draft']:
                    total_request_amount += payment_order.request_amount
            rec.total_register_payment = total_register_payment
            rec.total_request_amount = total_request_amount
            rec.due_amount = rec.amount_total - total_register_payment

    def action_fetch_carrier_shipping_rates(self):
        _logger.info(f"=> [TRACING] action_fetch_carrier_shipping_rates")

        partner_invoice_id = self.partner_invoice_id
        customer_name = partner_invoice_id.display_name
        customer_email = partner_invoice_id.email
        customer_street = partner_invoice_id.street
        customer_street2 = partner_invoice_id.street2
        customer_city = partner_invoice_id.city
        customer_zip = partner_invoice_id.zip
        customer_country_code = partner_invoice_id.country_code
        customer_phone = partner_invoice_id.phone

        partner_shipping_id = self.partner_shipping_id
        commercial_partner_shipping_id = partner_shipping_id
        shipping_name = commercial_partner_shipping_id.display_name
        shipping_street = commercial_partner_shipping_id.street
        shipping_street2 = commercial_partner_shipping_id.street2
        shipping_city = commercial_partner_shipping_id.city
        shipping_zip = commercial_partner_shipping_id.zip
        shipping_country_code = commercial_partner_shipping_id.country_code
        shipping_phone = commercial_partner_shipping_id.phone

        _logger.info(f"=> [TRACING] partner_invoice_id = {partner_invoice_id}")

        customer = {
            "email": customer_email,
            "default_address": {
                "first_name": customer_name,
                "last_name": "",
                "company": "",
                "address1": customer_street,
                "address2": customer_street2,
                "city": customer_city,
                "province": "",
                "zip": customer_zip,
                "phone": customer_phone,
                "name": customer_name,
                "province_code": "",
                "country": customer_country_code,
            }
        }

        destination = {
            "first_name": shipping_name,
            "phone": shipping_phone,
            "city": shipping_city,
            "zip": shipping_zip,
            "province": "",
            "last_name": "",
            "address1": shipping_street,
            "address2": shipping_street2,
            "company": "",
            # "latitude": 22.6566699,
            # "longitude": 114.01995,
            "name": shipping_name,
            "country": shipping_country_code,
            "province_code": ""
        }

        # NOTE used for local testing purposes only
        # line_items = [
        #     {
        #         "fulfillment_service": "manual",
        #         "grams": 15,
        #         "name": "0-5V Interface Module STMicroelectronics LM2902 | RAK5811",
        #         "price": "8.00",
        #         "product_id": 7763254640893,
        #         "properties": [],
        #         "quantity": 20,
        #         "requires_shipping": True,
        #         "sku": "100014",
        #         "taxable": True,
        #         "variant_id": 43046777028861,
        #         "vendor": "RAKwireless",
        #     }
        # ]

        line_items = []
        for line in self.order_line:
            taxable = False
            barcode = line.product_id.barcode

            if line.tax_id and line.tax_id.active:
                taxable = True

            total_price = decimal.Decimal(line.price_total) * decimal.Decimal(line.product_qty)

            # NOTE: Used for local testing only (as `x_studio_billable_weight`) is missing in my local DB.
            # weight = decimal.Decimal(line.product_id.weight)
            weight = decimal.Decimal(line.product_id.x_studio_billable_weight)
            processed_weight = weight * 1000
            weight_in_grams = str(processed_weight.quantize(decimal.Decimal('.01')))

            line_items.append({
                "fulfillment_service": "manual",
                "grams": weight_in_grams,
                "name": line.product_id.display_name,
                "price": str(total_price.quantize(decimal.Decimal('.01'))),
                "product_id": barcode,
                "properties": [],
                "quantity": line.product_qty,
                "requires_shipping": True,
                "sku": line.x_studio_pid,
                "taxable": taxable,
                "variant_id": line.x_studio_pid,  # Just because the carrier API expects this field.
                "vendor": "RAKwireless",
            })

        rates = self.fetch_shipping_fee(customer, destination, line_items)
        _logger.info(f"=> [TRACING] fetch_shipping_fee={rates}")

        rates = rates["rates"]
        _logger.info(f"=> [TRACING] prepare_shopify_order_vals rates={rates}")

        if len(rates) > 0:
            for rate_item in rates:
                if rate_item['service_name'] == "Global Standard Express (DAP)":
                    inner = rate_item
                    if all(k in inner for k in ("service_name",
                                                "service_code",
                                                "total_price",
                                                "currency",
                                                "description",
                                                "min_delivery_date",
                                                "max_delivery_date")):
                        total_price = decimal.Decimal(inner["total_price"] / 100.00) \
                            .quantize(decimal.Decimal('.01'))
                        carrier_rates = {
                            "x_studio_shipping_rates_service_name": inner["service_name"],
                            "x_studio_shipping_rates_service_code": inner["service_code"],
                            "x_studio_shipping_rates_total_price": total_price,
                            "x_studio_shipping_rates_currency": inner["currency"],
                            "x_studio_shipping_rates_description": inner["description"],
                            "x_studio_shipping_rates_min_delivery_date": self.format_timestamp(inner["min_delivery_date"]),
                            "x_studio_shipping_rates_max_delivery_date": self.format_timestamp(inner["max_delivery_date"]),
                        }

                        _logger.info(f"=> [TRACING] action_fetch_carrier_shipping_rates "
                                     f"carrier_rates={carrier_rates}")

                        self.write(carrier_rates)
                elif rate_item['service_name'] == "CN-US Express Line (DDP)":
                    _logger.info(f"=> [TRACING] action_fetch_carrier_shipping_rates: CN-US Express Line (DDP) is "
                                 f"intentionally ignored")
                else:
                    _logger.info(f"=> [TRACING] action_fetch_carrier_shipping_rates: {rate_item['service_name']} is "
                                 f"not explicitly handled")
        else:
            _logger.warning(f"=> [TRACING] action_fetch_carrier_shipping_rates: "
                            f"No Shipping Rates Available")

            self.notify_current_user("Unable to fetch Shipping rates, please check Invoice and Shipping "
                                     "addresses.  It is possible, the external service cannot provide any valid rate "
                                     "details for the chosen shipping destination.",
                                     "Alert", False)

            carrier_rates = {
                "x_studio_shipping_rates_service_name": "",
                "x_studio_shipping_rates_service_code": "",
                "x_studio_shipping_rates_total_price": "",
                "x_studio_shipping_rates_currency": "",
                "x_studio_shipping_rates_description": "",
                "x_studio_shipping_rates_min_delivery_date": "",
                "x_studio_shipping_rates_max_delivery_date": "",
            }
            self.write(carrier_rates)

    def format_timestamp(self, input):
        new_date = datetime.strptime(input, '%Y-%m-%d %H:%M:%S %z')
        formatted_date = new_date.strftime('%H:%M:%S, %a %b %d, %Y')

        return formatted_date

    def fetch_shipping_fee(self, customer, destination, line_items):
        service_rates_parser = ShopifyParserForCarrierServiceRates()
        rates = service_rates_parser.process(customer, destination, line_items)

        return rates

    # END fetch_shipping_fee

    def action_advance_payment_sale_order(self):
        _logger.info("=> action_advance_payment_sale_order")

        # active_ids = self.env.context.get('active_ids', [])
        # print("aaaaaaaaaaaaaaaaaaaaaaaaaaa", active_ids)
        list_order = []
        for order_id in self:
            sale_order_wizard_id = self.env['sale.order.wizard'].create({
                'sale_order_id': order_id.id
            })
            list_order.append(sale_order_wizard_id.id)

        view_id = self.env.ref('register_payment_sale.view_advance_payment_dorsan').id
        return {
            'name': _('Sale Order Payment Request'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'advance.payment.dorsan',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_sale_order_ids': [(6, 0, list_order)],
            }
        }

    @api.depends('advance_account_payment_ids', 'advance_account_payment_ids.state')
    def advance_payment(self):
        _logger.info("=> advance_payment")

        for rec in self:
            rec._get_total_register_payment()
            rec.advance_payment_count = len(
                rec.advance_account_payment_ids.filtered(lambda payment: payment.state != 'cancelled'))

    def action_view_advance_payment(self):
        _logger.info("=> action_view_advance_payment")

        payments = self.mapped('advance_account_payment_ids')
        action = self.env.ref('account.action_account_payments').read()[0]
        action['context'] = {
            'default_payment_type': 'inbound',
            'default_partner_type': 'customer',
            # 'search_default_inbound_filter': 1,
            'res_partner_search_mode': 'customer',
        }
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            form_view = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = payments.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def generate_simple_notification(self, message="", title="Alert", sticky=True, warning=True):
        bus_bus_obj = self.env["bus.bus"]
        bus_bus_obj._sendone(self.env.user.partner_id,
                             'simple_notification',
                             {
                                 "title": title,
                                 "message": message,
                                 "sticky": sticky,
                                 "warning": warning}
                             )

    def notify_current_user(self, message="", title="Alert", sticky=True, warning=True):
        return self.generate_simple_notification(message, title, sticky, warning)

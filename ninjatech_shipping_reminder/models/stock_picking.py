from datetime import date
from base64 import b64encode
import xlsxwriter
from io import BytesIO
from bs4 import BeautifulSoup

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_mail_sent = fields.Boolean(default=False)
    operation_type_name = fields.Char(related="picking_type_id.name")
    company_name = fields.Char(related="company_id.name")

    @api.model
    def ir_cron_stock_picking_done(self):
        after_date = date(day=28, month=3, year=2024)
        # done_picking_records = self.search([('state', '=', 'done'),
        #                                     ("date_done", '>', after_date),
        #                                     ('carrier_tracking_ref', '!=', False),
        #                                     ('carrier_id', '!=', False),
        #                                     ('is_mail_sent', '!=', True),
        #                                     ('picking_type_code', '=', 'outgoing'),
        #                                     ('operation_type_name', 'ilike', 'RAK-Delivery Orders'),
        #                                     ('company_name', 'ilike', 'Shenzhen Rakwireless')
        #                                     ], limit=100)
        done_picking_records = self.search([('state', '=', 'done')])
        attachment_obj = self.env['ir.attachment']
        print("recs...............", done_picking_records)
        for rec in done_picking_records:
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)

            if rec.x_serials_summary:
                worksheet = workbook.add_worksheet()
                soup = BeautifulSoup(rec.x_serials_summary)
                table = [[col.text for col in row.findAll('td')] for row in soup.findAll('tr')]
                print("finalllll", table)

                for index, row in enumerate(table):
                    for col_index, col in enumerate(row):
                        worksheet.write(index, col_index, col)

            if rec.x_deveui_summary:
                worksheet = workbook.add_worksheet()
                soup = BeautifulSoup(rec.x_deveui_summary)
                table = [[col.text for col in row.findAll('td')] for row in soup.findAll('tr')]
                for index, row in enumerate(table):
                    for col_index, col in enumerate(row):
                        worksheet.write(index, col_index, col)

            workbook.close()

            content = output
            data = b64encode(content.getvalue())

            attachment_data = attachment_obj.search([('name', '=', 'order.csv'),
                                                     ('description', '=', '__TO_REMOVE__')],
                                                    limit=1)
            if attachment_data:
                attachment_data.write({
                    'datas': data
                })
            else:
                attachmentData = {
                    'name': "order.csv",
                    'type': 'binary',
                    'datas': data,
                    'description': '__TO_REMOVE__'
                }
                attachment_data = attachment_obj.create(attachmentData)

            customer_name = rec.partner_id.name or rec.sale_id.partner_id.name
            customer_email = rec.partner_id.email or rec.sale_id.partner_id.email
            email_template = self.env.ref('ninjatech_shipping_reminder.pick_done_email_notification')
            email_template.attachment_ids = [(6, 0, [attachment_data.id])]
            email_template.send_mail(rec.id)
            rec.is_mail_sent = True

    def toCsv(self, csv):
        cSep = ","
        lSep = "\n"

        # Concat
        res = []
        for r in csv:
            f = []
            for c in r:
                cleaned = str(c).replace(',', '')

                f.append(cleaned)
            res.append(cSep.join(f))
        return lSep.join(res)

    # # Convert list to csv attachement (base 64)
    # def toAttachmentData(rows, filename):
    #     content = toCsv(rows)
    #
    #     # alert(content)
    #     data = b64encode(content.encode("utf-8-sig"))
    #
    #     attachmentData = {
    #         'name': filename,
    #         'type': 'binary',
    #         'datas': data,
    #         'description': '__TO_REMOVE__'
    #     }
    #     return attachmentData
    #
    #

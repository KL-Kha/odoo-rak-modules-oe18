from datetime import datetime, timedelta

from odoo import api, fields, models


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    purchase_qty_ordered = fields.Float(compute='_compute_purchase_ordered_qty',
                                        string='Ordered Quantities')



    @api.model
    def _purchase_requisition_reminder_cron(self):
        today_date = datetime.now()
        within_5_days = today_date - timedelta(days=5)
        purchase_requisition_line_rec = self.env['purchase.requisition'].sudo().search([('date_start', '<=', today_date),
                                                            ('date_end', '>=', within_5_days)])
        purchase_requisition = {}
        for rec in purchase_requisition_line_rec.line_ids:
            if rec.purchase_qty_ordered == 0:
                partner_id = rec.requisition_id.user_id.partner_id.id
                requisition_name = rec.requisition_id.name
                partner_id_val = purchase_requisition.get(rec.requisition_id.user_id.partner_id.id)
                purchase_requisition_name_val = partner_id_val and \
                                                partner_id_val.get(rec.requisition_id.name)

                if partner_id_val:
                    if purchase_requisition_name_val:
                        purchase_requisition[partner_id][requisition_name].append(
                            (rec.product_id.name,rec.requisition_id.date_start))
                    else:
                        print("purchase_requisition.............", purchase_requisition, partner_id)
                        purchase_requisition[partner_id].update({
                            rec.requisition_id.name: [(rec.product_id.name,rec.requisition_id.date_start)]
                        })
                else:
                    purchase_requisition[partner_id] = {
                        requisition_name: [(rec.product_id.name, rec.requisition_id.date_start)]
                    }


        for key, value in purchase_requisition.items():
            partner_id = self.env['res.partner'].browse(key)
            mail_template = self.env.ref(
                'ninjatech_purchase_agreement_notification.purchase_requisition_reminder_mail')
            print("partner email...", partner_id.email)
            mail_template.with_context({
                "list_of_agreement_lines": value,
                "partner_email": partner_id.email,
                "partner_name": partner_id.name
            }).send_mail(self.id, force_send=True)



    @api.depends('requisition_id.purchase_ids.state')
    def _compute_purchase_ordered_qty(self):
        line_found = set()
        for line in self:
            total = 0.0
            for po in line.requisition_id.purchase_ids.filtered(
                    lambda purchase_order: purchase_order.state != 'cancel'):
                for po_line in po.order_line.filtered(lambda order_line: order_line.product_id == line.product_id):
                    if po_line.product_uom != line.product_uom_id:
                        total += po_line.product_uom._compute_quantity(po_line.product_qty, line.product_uom_id)
                    else:
                        total += po_line.product_qty
            if line.product_id not in line_found:
                line.purchase_qty_ordered = total
                line_found.add(line.product_id)
            else:
                line.purchase_qty_ordered = 0

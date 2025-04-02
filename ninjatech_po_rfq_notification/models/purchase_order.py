import logging
from datetime import datetime, timedelta

from odoo import api, models, _
from markupsafe import Markup


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _rfq_reminder_cron(self):
        logging.info('Start RFQ scheduler.')
        within_3_days_date = datetime.now() - timedelta(days=3)
        today_date = datetime.now()
        rfq_purchase_order = self.search([('state', '=', 'draft'),
                                               ('date_planned', '<=', today_date),
                                               ('date_planned', '>=', within_3_days_date)
                                               ])
        odoobot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")

        logging.info(f'Purchase Order: {[o.name for o in rfq_purchase_order]}.')

        for rec in rfq_purchase_order:
            if rec.user_id:
                rec.message_post(body=Markup(_('Hi <a href=# data-oe-model=res.users data-oe-id=%d>@%s</a>, <br /> 这个RFQ单快到要求的交期了，但是还没审核完（没有IN单）\
                                           ，为了仓库能及时收货上架，请你及时进系统查看并处理，谢谢！')) % (rec.user_id.partner_id.id,rec.user_id.partner_id.name),
                                 message_type='notification',
                                 subtype_xmlid='mail.mt_note',
                                 author_id=odoobot_id,
                                 partner_ids=[rec.user_id.partner_id.id]
                                 )

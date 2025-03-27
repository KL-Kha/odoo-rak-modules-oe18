# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)

class PortalShare(models.TransientModel):
    _inherit = 'portal.share'

    @api.depends('res_model', 'res_id')
    def _compute_share_link(self):
        for rec in self:
            res_model = self.env[rec.res_model]

            externalDomain = self.env['ir.config_parameter'].sudo().get_param('mjb_portal_share.external_domain')
            
            if isinstance(res_model, self.pool['portal.mixin']):
                record = res_model.browse(rec.res_id)
                url = record.get_base_url()
                if externalDomain:
                    url = externalDomain
                rec.share_link = url + record._get_share_url(redirect=True)
# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Controller, content_disposition
# from odoo.http import request, route, Controller
# from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape
import json
import logging

_logger = logging.getLogger(__name__)


class BOMStructureontroller(Controller):
    @http.route(['/fal_bom_xls_report/download'], type='http', auth="user")
    def get_report_xlsx(self, data, unfolded, token=False):
        xlsx_report_model = request.env['report.mrp.report_bom_structure']
        try:
            response = request.make_response(
                None,
                headers=[
                    ('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', content_disposition('bom_structure_cost' + '.xlsx'))
                ]
            )
            response.stream.write(xlsx_report_model.generate_xlsx_report(data, unfolded))
            response.set_cookie('fileToken')
            return response
        except Exception as e:
            se = http.serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))

# -*- coding: utf-8 -*-
# © 2015 Gael Rabier, Pierre Faniel, Jérôme Guerriat
# © 2015 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import logging
import os
import tempfile

import io
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval as eval
from PyPDF2 import PdfFileWriter, PdfFileReader

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        fields_obj = self.env['ir.model.fields']
        active_model = self.env.context.get('active_model',False)
        model = active_model if active_model else self.model
        obj = self.env['ir.model'].search([('model', '=', model)])
        contract_condition_report_id = fields_obj.search([('model_id', '=', obj.id), ('name', '=', 'contract_condition_report_id')])
        context = dict(self._context)
        if contract_condition_report_id:
            if len(res_ids) > 1:
                temporary_files = []
                for docid in res_ids:
                    report_pdf = super(IrActionsReport, self)._render_qweb_pdf(report_ref, docid, data)
                    pdf_incl_terms = report_pdf
                    if not context.get('add_condition'):
                        pdf_incl_terms = self.add_condition(report_ref, [docid], report_pdf)

                    pdfreport_fd, pdfreport_path = tempfile.mkstemp(
                        suffix='.pdf', prefix='report.tmp.')
                    os.write(pdfreport_fd, pdf_incl_terms[0])
                    os.close(pdfreport_fd)

                    temporary_files.append(pdfreport_path)

                pdf_writer = PdfFileWriter()
                for path in temporary_files:
                    pdf_reader = PdfFileReader(path)
                    for page in range(pdf_reader.getNumPages()):
                        pdf_writer.addPage(pdf_reader.getPage(page))
                stream_to_write = io.BytesIO()
                pdf_writer.write(stream_to_write)

                pdf_content = stream_to_write.getvalue()
                for temporary_file in temporary_files:
                    try:
                        os.unlink(temporary_file)
                    except (OSError, IOError):
                        _logger.error(
                            'Error when trying to remove file %s'
                            % temporary_file)
                return pdf_content, 'pdf'
            else:
                report_pdf = super(IrActionsReport, self)._render_qweb_pdf(report_ref, res_ids, data)
                if not context.get('add_condition'):
                    return self.add_condition(report_ref, res_ids, report_pdf)
                else:
                    return report_pdf
        else:
            return super(IrActionsReport, self)._render_qweb_pdf(report_ref, res_ids, data)

    @api.model
    def add_condition(self, report_ref, res_id, original_report_pdf):
        active_model = self.env.context.get('active_model',False)
        model = active_model if active_model else self.model
        object = self.env[model].browse(res_id)

        report = self._get_report_from_name(object.contract_condition_report_id.report_name)

        if report:
            pdf = report.with_context(add_condition=True)._render_qweb_pdf(report_ref,res_id)[0]

            if pdf:
                writer = PdfFileWriter()
                stream_original_report = io.BytesIO(original_report_pdf[0])
                reader_original_report = PdfFileReader(stream_original_report)
                stream_terms_and_conditions = io.BytesIO(
                    pdf)
                reader_terms_and_conditions = PdfFileReader(
                    stream_terms_and_conditions)
                for page in range(0, reader_original_report.getNumPages()):
                    writer.addPage(reader_original_report.getPage(page))

                for page in range(0, reader_terms_and_conditions.getNumPages()):
                    writer.addPage(reader_terms_and_conditions.getPage(page))

                stream_to_write = io.BytesIO()
                writer.write(stream_to_write)

                combined_pdf = stream_to_write.getvalue()
                return combined_pdf, 'pdf'
            else:
                return original_report_pdf
        else:
            return original_report_pdf

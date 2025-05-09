# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.tools.misc import xlsxwriter
import io
import json

import logging

_logger = logging.getLogger(__name__)


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'
    _description = "BOM XLSX Report"

    def _get_xls_line(self, bom_id, qty=1, level=0):
        bom = self.env['mrp.bom'].browse(bom_id)
        if self.env.context.get('warehouse_id'):
            warehouse = self.env['stock.warehouse'].browse(self.env.context.get('warehouse_id'))
        else:
            warehouse = self.env['stock.warehouse'].browse(self.get_warehouses()[0]['id'])
        data = self._get_bom_data(bom=bom_id,warehouse=warehouse, line_qty=qty, bom_line=False)
        xls_line = []
        xls_line.append((level, data['name'], 'Component', data['name'], data['quantity'], data['uom_name'], data['prod_cost'], data['bom_cost']))
        level = level + 1
        for component in data['components']:
            if 'child_bom' in component and component['child_bom']:
                child_xls_lines = self._get_xls_line(bom_id=component['child_bom'], qty=component['prod_qty'], level=level)
                for child_xls_line in child_xls_lines:
                    xls_line.append(child_xls_line)
            else:
                xls_line.append((level, component['name'], 'Component', '', component['quantity'], component['uom_name'], component['prod_cost'], component['bom_cost']))
        for operation in data['operations']:
            xls_line.append((level, operation['name'], 'Operation', '', operation['duration_expected'], 'Minutes', '', operation['total']))
        return xls_line

    def generate_xlsx_report(self, bom_id, unfolded):
        data = self._get_report_data(int(bom_id))
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("BoM Structure & Cost")
        workbook.add_format({"bold": True})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True})
        sheet.set_column(0, 9, 20)
        sheet.write(0, 0, 'BoM Structure & Cost', title_style)
        sheet.write(1, 0, data['lines']['code'], title_style)

        get_line = self._get_xls_line(data['lines']['bom'], qty=data['lines']['quantity'], level=1)

        # Get highest level
        highest_level = 0
        for line in get_line:
            if line[0] > highest_level:
                highest_level = line[0]
        # Write value of line
        row = 4
        for line in get_line:
            # Is line Component / Operation
            sheet.write(row, 0, line[2])
            # Level
            sheet.write(row, line[0], line[1])
            # BOM
            sheet.write(row, 1 + highest_level, line[3])
            # Quantity
            sheet.write(row, 2 + highest_level, line[4])
            # UoM
            sheet.write(row, 3 + highest_level, line[5])
            # Prod Cost
            sheet.write(row, 4 + highest_level, line[6])
            # Total
            sheet.write(row, 5 + highest_level, line[7])
            row += 1

        sheet_title = [
            _("BOM Component/Operation"),
        ]
        x = 0
        while x < highest_level:
            sheet_title.append(_("Level " + str(x)))
            x += 1
        sheet_title.append(_("BoM"))
        sheet_title.append(_("Quantity"))
        sheet_title.append(_("Unit of Measure"))
        sheet_title.append(_("Product Cost"))
        sheet_title.append(_("BoM Cost"))
        sheet.write_row(3, 0, sheet_title)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()
        return generated_file

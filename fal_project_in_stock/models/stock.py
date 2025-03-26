from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fal_project_numbers = fields.Char(compute='_get_projects', string='Project Numbers', help='The projects.', store=True)

    @api.depends('move_ids', 'move_ids.fal_project_id')
    def _get_projects(self):
        for picking in self:
            temp = []
            for line in picking.move_ids:
                if line.fal_project_id and line.fal_project_id.code not in temp:
                    temp.append(line.fal_project_id.code or line.fal_project_id.name)
            if temp:
                picking.fal_project_numbers = "; ".join(temp)
            else:
                picking.fal_project_numbers = ""


class StockMove(models.Model):
    _inherit = "stock.move"

    fal_project_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
        res = super(StockMove, self)._generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description)
        res['debit_line_vals'].update({
            'analytic_account_id': self.fal_project_id.id
        })
        res['credit_line_vals'].update({
            'analytic_account_id': self.fal_project_id.id
        })
        return res

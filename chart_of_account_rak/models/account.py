from odoo import api, fields, models

class AccountAccount(models.Model):
    _inherit = 'account.account'

    analytic_plan_id = fields.Many2one('account.analytic.plan', string="Analytic Plan")
    is_analytic_account = fields.Boolean('Is Analytic Account')
    is_hr_department = fields.Boolean('Is HR Department Account')
    is_partner = fields.Boolean('Is Partner Account')

    @api.onchange('is_analytic_account')
    def _onchange_is_analytic_account(self):
        for rec in self:
            if not rec.is_analytic_account:
                rec.analytic_plan_id = False

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_analytic_account = fields.Boolean(string='Is Analytic Account', related='account_id.is_analytic_account', readonly=True)
    analytic_plan_id = fields.Many2one('account.analytic.plan', string="Analytic Plan", related='account_id.analytic_plan_id', readonly=True)
    is_hr_department = fields.Boolean('Is HR Department Account', related='account_id.is_hr_department', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    hr_department_id = fields.Many2one('hr.department', string='Department')
    is_partner = fields.Boolean('Is Partner Account', related='account_id.is_partner', readonly=True)

    @api.onchange('employee_id', 'partner_id')
    def _onchange_employee_or_partner(self):
        for rec in self:
            if rec.partner_id:
                employee = self.env['hr.employee'].search([('partner_id', '=', rec.partner_id.id)], limit=1)
                if employee:
                    rec.employee_id = employee.id
            if rec.employee_id and rec.employee_id.partner_id:
                rec.partner_id = rec.employee_id.partner_id
                rec.hr_department_id = rec.employee_id.department_id.id

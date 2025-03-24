from odoo import fields, models, api, _


class AccountAccountTag(models.Model):
    _inherit = "account.account.tag"

    x_code = fields.Char(string="Tag Code")


# class AccountChartTemplate(models.Model):
#     _inherit = "account.chart.template"
#
#     @api.model
#     def _create_cash_discount_loss_account(self, company, code_digits):
#         res = super(AccountChartTemplate, self)._create_cash_discount_loss_account(
#             company, code_digits)
#         if self == self.env.ref("mjb_l10n_cn.l10n_gen_chart_china"):
#             res.write({
#                 "tag_ids": [(4, self.env.ref('mjb_l10n_cn.mjb_data_account_tag_overhead_expenses').id)],
#                 "currency_id":  self.env.ref("base.CNY").id,
#             })
#             self.env['ir.model.data'].create({
#                 'name': 'gen_chart999998',
#                 'module': 'mjb_l10n_cn',
#                 'model': res._name,
#                 'res_id': res.id,
#             })
#         return res
#
#     @api.model
#     def _create_cash_discount_gain_account(self, company, code_digits):
#         res = super(AccountChartTemplate, self)._create_cash_discount_gain_account(
#             company, code_digits)
#         if self == self.env.ref("mjb_l10n_cn.l10n_gen_chart_china"):
#             res.write({
#                 "tag_ids": [(4, self.env.ref('mjb_l10n_cn.mjb_data_account_tag_revenue').id)],
#                 "currency_id":  self.env.ref("base.CNY").id,
#                 "account_type": "income",
#             })
#             self.env['ir.model.data'].create({
#                 'name': 'gen_chart999997',
#                 'module': 'mjb_l10n_cn',
#                 'model': res._name,
#                 'res_id': res.id,
#             })
#         return res

# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('mjb_l10n_cn')
    def _get_mjb_l10n_cn_template_data(self):
        return {
            'name': '中国会计科目表 (详细版）|| Majorbird Chinese CoA',
            'country': None,
            'use_anglo_saxon': True,
            'code_digits': 0,
            'property_account_receivable_id': 'mjb_l10n_cn_11220000',
            'property_account_payable_id': 'mjb_l10n_cn_22020000',
            'property_account_expense_categ_id': 'mjb_l10n_cn_66020000',
            'property_account_income_categ_id': 'mjb_l10n_cn_60010000',
        }

    @template('mjb_l10n_cn', 'res.company')
    def _get_mjb_l10n_cn_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.cn',
                'bank_account_code_prefix': 'GBAP',
                'cash_account_code_prefix': 'GCAP',
                'transfer_account_code_prefix': '580',
                'account_default_pos_receivable_account_id': 'mjb_l10n_cn_11220000',
                'income_currency_exchange_account_id': 'mjb_l10n_cn_60610000',
                'expense_currency_exchange_account_id': 'mjb_l10n_cn_60610000',
            },
        }

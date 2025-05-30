# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    origin_country_ept = fields.Many2one('res.country', string='Origin Country',
                                         help="Warehouse country based on sales order warehouse country system will "
                                              "apply fiscal position")

    # @api.model
    # def _get_fpos_by_region(self, country_id=False, state_id=False, zipcode=False, vat_required=False):
    #     """
    #     Inherited this method for selecting fiscal position based on warehouse (origin country).
    #     :param: res.country() id
    #     :param: res.state() id
    #     :param: zip code
    #     :param: True/False
    #     :return: account.fiscal.position()
    #     """
    #     origin_country_id = self._context.get('origin_country_ept', False)
    #     if not origin_country_id:
    #         return super(AccountFiscalPosition, self)._get_fpos_by_region(country_id=country_id, state_id=state_id,
    #                                                                       zipcode=zipcode, vat_required=vat_required)
    #     return self.search_fiscal_position_based_on_origin_country(origin_country_id, country_id, state_id, zipcode,
    #                                                                vat_required)

    @api.model
    def search_fiscal_position_based_on_origin_country(self, origin_country_id, country_id, state_id, zipcode,
                                                       vat_required):
        """
        Search fiscal position based on origin country
        [UPD] Check all base conditions for search fiscal position as per base and with origin country.
        :param origin_country_id: Warehouse-partner-country_id OR Warehouse-company-partner-country_id or False
        :param country_id: delivery country id
        :param state_id: delivery state id
        :param zipcode: delivery zip code
        :param vat_required: True / False
        :return: fpos object
        """
        if not country_id:
            return False
        if self._context.get('is_b2b_amz_order', False):
            vat_required = self._context.get('is_b2b_amz_order', False)
        base_domain = [('vat_required', '=', vat_required), ('company_id', 'in', [self.env.company.id, False]),
                       ('origin_country_ept', 'in', [origin_country_id, False])]
        null_state_dom = state_domain = [('state_ids', '=', False)]
        null_zip_dom = zip_domain = [('zip_from', '=', False), ('zip_to', '=', False)]
        null_country_dom = [('country_id', '=', False), ('country_group_id', '=', False)]
        is_amazon_fpos = self._context.get('is_amazon_fpos', False)
        if is_amazon_fpos:
            base_domain.append(('is_amazon_fpos', '=', is_amazon_fpos))
        is_bol_fpos = self._context.get('is_bol_fpos', False)
        if is_bol_fpos:
            base_domain.append(('is_bol_fiscal_position', '=', is_bol_fpos))
        if zipcode:
            zip_domain = [('zip_from', '<=', zipcode), ('zip_to', '>=', zipcode)]
        if state_id:
            state_domain = [('state_ids', '=', state_id)]
        domain_country = base_domain + [('country_id', '=', country_id)]
        domain_group = base_domain + [('country_group_id.country_ids', '=', country_id)]
        # Build domain to search records with exact matching criteria
        fpos = self.search(domain_country + state_domain + zip_domain, limit=1)
        # return records that fit the most the criteria, and fallback on less specific fiscal positions if any can be
        # found
        if not fpos and state_id:
            fpos = self.search(domain_country + null_state_dom + zip_domain, limit=1)
        if not fpos and zipcode:
            fpos = self.search(domain_country + state_domain + null_zip_dom, limit=1)
        if not fpos and state_id and zipcode:
            fpos = self.search(domain_country + null_state_dom + null_zip_dom, limit=1)
        # fallback: country group with no state/zip range
        if not fpos:
            fpos = self.search(domain_group + null_state_dom + null_zip_dom, limit=1)
        if not fpos:
            # Fallback on catchall (no country, no group)
            fpos = self.search(base_domain + null_country_dom, limit=1)
        return fpos

    @api.model
    def _get_fiscal_position(self, partner, delivery=None):
        """
        Override this method for apply common connector logic to find and set fiscal position in the
        order as per connector wise request.
        :param: partner: res.partner() (order partner)
        :param: delivery: res.partner() (delivery partner)
        :return: fiscal position found (recordset)
        TODO : In future we need to improve the common connector apply fiscal position flow as per default v18 flow.
        """
        origin_country_id = self._context.get('origin_country_ept', False)
        if not partner:
            return self.env['account.fiscal.position']

        company = self.env.company
        intra_eu = vat_exclusion = False
        if company.vat and partner.vat:
            eu_country_codes = set(self.env.ref('base.europe').country_ids.mapped('code'))
            intra_eu = company.vat[:2] in eu_country_codes and partner.vat[:2] in eu_country_codes
            vat_exclusion = company.vat[:2] == partner.vat[:2]

        # If company and partner have the same vat prefix (and are both within the EU), use invoicing
        if not delivery or (intra_eu and vat_exclusion):
            delivery = partner

        # partner manually set fiscal position always win
        manual_fiscal_position = (
            delivery.with_company(company).property_account_position_id
            or partner.with_company(company).property_account_position_id
        )
        if manual_fiscal_position:
            return manual_fiscal_position

        if not partner.country_id:
            return self.env['account.fiscal.position']
        # if we find origin_country_id then we consider the common connector flow for apply fiscal position
        if origin_country_id:
            return self.search_fiscal_position_based_on_origin_country(
                origin_country_id, delivery.country_id.id, delivery.state_id.id, delivery.zip,
                (self._get_vat_valid(delivery, company)))
        else:
            # Search for a auto applied fiscal position matching the partner
            ranking_subfunctions = self._get_fpos_ranking_functions(delivery)
            def ranking_function(fpos):
                return tuple(rank[1](fpos) for rank in ranking_subfunctions)

            all_auto_apply_fpos = self.search(self._check_company_domain(self.env.company) + [('auto_apply', '=', True)])
            fpo_with_ranking = ((fpos, ranking_function(fpos)) for fpos in all_auto_apply_fpos)
            valid_auto_apply_fpos = filter(lambda x: all(x[1]), fpo_with_ranking)
            return max(
                valid_auto_apply_fpos,
                key=lambda x: x[1],
                default=(self.env['account.fiscal.position'], False)
            )[0]

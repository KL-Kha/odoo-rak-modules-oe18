
from odoo import models
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):

    _inherit = "product.template"

    # def _get_product_accounts(self):
    #     """ Add the stock accounts related to product to the result of super()
    #     @return: dictionary which contains information regarding stock accounts and super (income+expense accounts)
    #     """
    #     accounts = super(ProductTemplate, self)._get_product_accounts()
    #     res = self._get_asset_accounts()
    #     accounts.update({
    #         'stock_input': res['stock_input'] or self.categ_id.property_stock_account_input_categ_id,
    #         'stock_output': res['stock_output'] or self.categ_id.property_stock_account_output_categ_id,
    #         'stock_valuation': self.categ_id.property_stock_valuation_account_id or False,
    #     })
    #     return accounts


    def get_product_accounts(self, fiscal_pos=None, is_subcontract=False):
        """ Add the stock journal related to product to the result of super()
        @return: dictionary which contains all needed information regarding stock accounts and journal and super (income+expense accounts)
        """
        accounts = super(ProductTemplate, self).get_product_accounts(fiscal_pos=fiscal_pos)
        _logger.info(f"This is product account method subcontract:{is_subcontract}")
        if is_subcontract:
            # accounts.update({'stock_valuation': self.categ_id.subcontracted_valuation_account_id or False})
            accounts.update({'stock_input': self.categ_id.subcontracted_material_account_id or False})
            accounts.update({'stock_subcontract_valuation': self.categ_id.subcontracted_valuation_account_id or False})

        return accounts


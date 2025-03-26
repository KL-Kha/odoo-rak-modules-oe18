from odoo import api, models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends('product_id')
    def compute_hscode(self):
        for rec in self:
            if rec.product_id.hs_code:
                rec.fal_hscode = rec.product_id.hs_code
            else:
                current_categ_id = rec.product_id.categ_id
                while not current_categ_id.fal_hscode_cat and current_categ_id.parent_id:
                    current_categ_id = current_categ_id.parent_id
                rec.fal_hscode = current_categ_id.fal_hscode_cat

    fal_hscode = fields.Char(
        string="HS Code",
        compute='compute_hscode',
        help="Standardized code for international\
        shipping and goods declaration")

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.depends('product_id')
    def compute_hscode(self):
        for rec in self:
            if rec.product_id.hs_code:
                rec.fal_hscode = rec.product_id.hs_code
            else:
                current_categ_id = rec.product_id.categ_id
                while not current_categ_id.fal_hscode_cat and current_categ_id.parent_id:
                    current_categ_id = current_categ_id.parent_id
                rec.fal_hscode = current_categ_id.fal_hscode_cat or False

    fal_hscode = fields.Char(
        string="HS Code",
        compute='compute_hscode', store=True,
        help="Standardized code for international\
        shipping and goods declaration")

    def _get_aggregated_product_quantities(self, **kwargs):
        """Returns dictionary of products and corresponding values of interest + hs_code

        Unfortunately because we are working with aggregated data, we have to loop through the
        aggregation to add more values to each datum. This extension adds on the hs_code value.

        returns: dictionary {same_key_as_super: {same_values_as_super, hs_code}, ...}
        """
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
        for aggregated_move_line in aggregated_move_lines:
            line = self.filtered(lambda a: a.product_id == aggregated_move_lines[aggregated_move_line]['product'])
            fal_hs_code = ''
            if len(line) > 1:
                fal_hs_code = line[0].fal_hscode
            else:
                fal_hs_code = line.fal_hscode

            aggregated_move_lines[aggregated_move_line]['fal_hscode'] = fal_hs_code
        return aggregated_move_lines

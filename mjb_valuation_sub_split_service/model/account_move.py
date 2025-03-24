from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_split_subcontracted_cost_mo_entry(self):
        for rec in self:
            rec.splitSubcontractCostEntry()

    def splitSubcontractCostEntry(self):
        # get related stock move
        stockMove = self.stock_move_id
        if not stockMove:
            print("No stock move")
            return False

        # get related production order for finished goods
        productionOrder = stockMove.production_id
        if not productionOrder:
            print("No production order")
            return False

        # If not subcontracting order that do nothing
        if productionOrder.picking_type_id.name != 'Subcontracting':
            print("Not subcontracting order")
            return False

        # get related product
        product = productionOrder.product_id
        print('product', product)
        if not product:
            print("No product")
            return False

        if productionOrder and not productionOrder.bom_id:
            return False

        if productionOrder and productionOrder.bom_id and productionOrder.bom_id.type != 'subcontract':
            return False

        # Get PO
        purchaseOrder = self.env['stock.picking'].search([
            ('name', '=', stockMove.group_id.name)
        ]).purchase_id
        if not purchaseOrder:
            print("No PO")
            return False

        # Get PO Line
        purchaseOrderLine = self.env['purchase.order.line'].search([
            ('order_id', '=', purchaseOrder.id),
            ('product_id', '=', product.id)
        ])
        

        MATERIAL_ACCOUNT_ID = product.categ_id.subcontracted_material_account_id.id
        LABOUR_ACCOUNT_ID = product.categ_id.subcontracted_valuation_account_id.id
        VALUATION_ACCOUNT_ID = product.categ_id.property_stock_valuation_account_id.id
        # MATERIAL_ACCOUNT_ID = stockMove.production_id.production_location_id.valuation_out_account_id.id
        # if not MATERIAL_ACCOUNT_ID:
            # MATERIAL_ACCOUNT_ID = product.categ_id.property_stock_account_output_categ_id.id
        if not LABOUR_ACCOUNT_ID:
            print("No subcontract valuation account")
            return False
        if not VALUATION_ACCOUNT_ID:
            print("No valuation account")
            return False
        if not MATERIAL_ACCOUNT_ID:
            print("No subcontract material account")
            return False

        # Find the debit line
        print("Can work")
        debitLine = False
        hasLabour = False
        for l in self.line_ids:
            if l.account_id.id == VALUATION_ACCOUNT_ID:
                debitLine = l
            if l.account_id.id == LABOUR_ACCOUNT_ID:
                hasLabour = True

        # only continue if not already done
        if hasLabour:
            print('has labour entries, skip')
            return False

        # get labour cost
        # workOrders = productionOrder.workorder_ids
        toCreate = []

        valuation_line_id = self.line_ids.filtered(lambda l: l.account_id.id == VALUATION_ACCOUNT_ID)

        if valuation_line_id:
            other_line_ids = self.line_ids.filtered(lambda l: l.account_id.id != VALUATION_ACCOUNT_ID)
            
            # Total product quantity from PO
            total_po_qty = purchaseOrderLine[0].product_qty or 1
            
            # Total valuation amount
            total_valuation = valuation_line_id.debit

            for other_line_id in other_line_ids:
                qty_ratio = other_line_id.quantity / total_po_qty
                material_cost = purchaseOrderLine[0].price_subtotal * qty_ratio
                labour_cost = (total_valuation - purchaseOrderLine[0].price_subtotal) * qty_ratio

                toCreate.append((0, 0, {
                    "quantity": other_line_id.quantity,
                    "credit": round(labour_cost / len(other_line_ids), 2),  # Divided among all lines
                    "debit": 0.0,
                    "account_id": LABOUR_ACCOUNT_ID,
                    "name": valuation_line_id.name.split('-')[0] + '- Service',
                    "currency_id": self.currency_id.id
                }))

                toCreate.append((0, 0, {
                    "quantity": other_line_id.quantity,
                    "credit": round(material_cost / len(other_line_ids), 2),  # Divided among all lines
                    "debit": 0.0,
                    "account_id": MATERIAL_ACCOUNT_ID,
                    "name": valuation_line_id.name.split('-')[0] + '- Material',
                    "currency_id": self.currency_id.id
                }))

                toCreate.append((0, 0, {
                    "quantity": other_line_id.quantity,
                    "credit": other_line_id.debit,
                    "debit": other_line_id.credit,
                    "account_id": valuation_line_id.account_id.id,
                    "name": valuation_line_id.name,
                    "currency_id": self.currency_id.id
                }))

        aggregated_values = {}

        for entry in toCreate:
            _, _, values = entry
            account_id = values['account_id']
            credit = values['credit']
            debit = values['debit']
            
            # If account_id already exists in the dictionary, update its values
            if account_id in aggregated_values:
                aggregated_values[account_id]['credit'] += credit
                aggregated_values[account_id]['debit'] += debit
            else:
                # If account_id is not present, add it to the dictionary
                aggregated_values[account_id] = {'credit': credit, 'debit': debit}

        # Create a new list with aggregated values
        group_toCreate = []
        for account_id, values in aggregated_values.items():
            group_toCreate.append((0, 0, {
                'quantity': next(values['quantity'] for _, _, values in toCreate if values['account_id'] == account_id),
                'credit': values['credit'],
                'debit': values['debit'],
                'account_id': account_id,
                # Assuming 'name' and 'currency_id' remain the same for each account_id
                'name': next(values['name'] for _, _, values in toCreate if values['account_id'] == account_id),
                'currency_id': next(values['currency_id'] for _, _, values in toCreate if values['account_id'] == account_id)
            }))

        oldLines = self.line_ids.mapped('id')
        if self.state == 'posted':
            self.sudo().button_draft()
            # self.env.cr.commit()

        from pprint import pprint
        pprint(group_toCreate)
        self.sudo().write({
            'line_ids': group_toCreate
        })
        # self.env.cr.commit()
        self.env['account.move.line'].sudo().browse(oldLines).unlink()
        self.sudo().action_post()
        return True

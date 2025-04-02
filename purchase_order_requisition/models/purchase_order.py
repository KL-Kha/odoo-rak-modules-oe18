from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('requisition_id')
    def onchange_requisition_id(self):
        for rec in self:
            for order_line in rec.order_line:
                order_line.unlink()

        if not self.requisition_id:
            return

        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_context(force_company=self.company_id.id)._get_fiscal_position(partner)
        fpos = FiscalPosition.browse(fpos)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id
        self.company_id = requisition.company_id.id
        self.currency_id = requisition.currency_id.id
        if not self.origin or requisition.name not in self.origin.split(', '):
            if self.origin:
                if requisition.name:
                    self.origin = self.origin + ', ' + requisition.name
            else:
                self.origin = requisition.name
        self.notes = requisition.description
        self.date_order = fields.Datetime.now()

        # if requisition.type_id.line_copy != 'copy':
        #     return

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context(
                lang=partner.lang,
                partner_id=partner.id
            )
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            if fpos:
                taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(
                    lambda tax: tax.company_id == requisition.company_id)).ids
            else:
                taxes_ids = line.product_id.supplier_taxes_id.filtered(
                    lambda tax: tax.company_id == requisition.company_id).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            # if requisition.type_id.quantity_copy != 'copy':
            #     product_qty = 0

            # Create PO line
            order_line_values = line._prepare_purchase_order_line(
                name=name, product_qty=product_qty, price_unit=price_unit,
                taxes_ids=taxes_ids)
            order_line_values.update({'purchase_requisition_line_id': line.id})
            order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines

class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    purchase_requisition_line_id = fields.Many2one('purchase.requisition.line', 'Purchase Requisition Line')


    # def write(self, vals):
    #     res = super(PurchaseOrder, self).write(vals)
    #     return res
    #
    # @api.model
    # def create(self, vals):
    #     rec = super(PurchaseOrder, self).create(vals)
    #     purchase_order_line_env = self.env['purchase.order.line']
    #     purchase_order_line_ids = purchase_order_line_env.search[('purchase_requisition_line_id', '=', rec.id)]
    #     qty_ordered = 0
    #     qty_received = 0
    #     for purchase_line in purchase_order_line_ids:
    #         qty_ordered += purchase_line.product_qty
    #         qty_received += purchase_line.qty_received
    #     rec.purchase_requisition_line_id.qty_ordered = qty_ordered
    #     rec.purchase_requisition_line_id.qty_received = qty_received
    #     return rec


class PurchaseRequisitionOrderLine(models.Model):

    _inherit = 'purchase.requisition.line'

    @api.depends('requisition_id.purchase_ids.state')
    def _compute_ordered_qty(self):
        for line in self:
            qty_ordered = 0
            qty_received = 0
            for po in line.requisition_id.purchase_ids.filtered(lambda purchase_order: purchase_order.state in ['purchase', 'done']):
                for po_line in po.order_line.filtered(lambda order_line: order_line.purchase_requisition_line_id.id == line.id):
                    qty_ordered += po_line.product_qty
                    qty_received += po_line.qty_received
            line.qty_ordered = qty_ordered
            line.qty_received = qty_received
            line.qty_remaining = line.product_qty - line.qty_ordered

    qty_received = fields.Float(string='Received Quantity', compute='_compute_ordered_qty')
    qty_remaining = fields.Float(string='Remmaining Quantity', compute='_compute_ordered_qty')






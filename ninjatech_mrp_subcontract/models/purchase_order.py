from odoo import models
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_picking(self):
        res = super()._prepare_picking()
        _logger.info(f"Prepare pikcing  :{self.picking_type_id.x_studio_operation_type_category}")
        if self.picking_type_id.x_studio_operation_type_category == "Outsourcing":
            res.update({
                'location_dest_id': self._get_destination_location(),
                'location_id': self.partner_id.property_stock_subcontractor.id
            })
        return res

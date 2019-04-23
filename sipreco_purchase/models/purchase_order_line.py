##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        price_unit = self.price_unit
        res = super(PurchaseOrderLine, self)._onchange_quantity()
        if self.order_id.requisition_id and self.order_id.\
                requisition_id.type_id.price_unit_copy != 'copy':
            self.price_unit = price_unit
        return res

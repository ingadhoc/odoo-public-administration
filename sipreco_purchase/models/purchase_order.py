##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        super(PurchaseOrder, self)._onchange_requisition_id()
        if self.requisition_id.type_id.line_copy == 'copy'\
                and self.requisition_id.type_id.price_unit_copy != 'copy':
            self.order_line.update({'price_unit': 0.0})

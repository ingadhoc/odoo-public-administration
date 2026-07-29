##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    brand = fields.Char(
    )

    def _compute_price_unit_and_date_planned_and_name(self):
        lines_with_requisition = self.filtered(lambda l: l.order_id.requisition_id)
        saved_prices = {pol.id: pol.price_unit for pol in lines_with_requisition}
        super()._compute_price_unit_and_date_planned_and_name()
        for pol in lines_with_requisition:
            pol.price_unit = saved_prices.get(pol.id, 0.0)

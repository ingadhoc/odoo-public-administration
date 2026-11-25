##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    brand = fields.Char(
    )
    requisition_line_id = fields.Many2one(
        'purchase.requisition.line',
        string='Requisition Item',
        copy=False,
        index='btree_not_null',
        ondelete='set null',
        help="Requisition line this line quotes. Lines added by hand with the same item are shown as alternatives "
             "in the price comparison.",
    )

    def _compute_price_unit_and_date_planned_and_name(self):
        lines_with_requisition = self.filtered(lambda l: l.order_id.requisition_id)
        saved_prices = {pol.id: pol.price_unit for pol in lines_with_requisition}
        super()._compute_price_unit_and_date_planned_and_name()
        for pol in lines_with_requisition:
            pol.price_unit = saved_prices.get(pol.id, 0.0)

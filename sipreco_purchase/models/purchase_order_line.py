##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    brand = fields.Char(
    )

    @api.depends('product_qty', 'product_uom', 'company_id', 'order_id.partner_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        price_no_update_lines = self.filtered(
            lambda line: line.order_id.requisition_id
        )
        res = super(PurchaseOrderLine, self - price_no_update_lines)._compute_price_unit_and_date_planned_and_name()
        return res

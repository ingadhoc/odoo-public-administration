##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    brand = fields.Char(
    )
<<<<<<< 8da170e4291c677153ba7ad93221f7f4c93a3a65

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        price_unit = self.price_unit
        res = super()._onchange_quantity()
        if self.order_id.requisition_id and self.order_id.\
                requisition_id.type_id.price_unit_copy != 'copy':
            self.price_unit = price_unit
        return res
||||||| 7453b8c4b324cac8e8c56a9705badc8e524dcbfa

    @api.depends('product_qty', 'product_uom', 'company_id', 'order_id.partner_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        price_no_update_lines = self.filtered(
            lambda line: line.order_id.requisition_id
        )
        res = super(PurchaseOrderLine, self - price_no_update_lines)._compute_price_unit_and_date_planned_and_name()
        return res
=======
>>>>>>> f522a8f10268cbe375bdf4e0fa7e3c1d689d2273

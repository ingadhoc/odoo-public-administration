##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    name = fields.Text(
    )
    price_unit = fields.Float(
        string='Unit Price',
        digits='Product Price',
    )
    subtotal = fields.Float(
        digits='Product Price',
        compute='_compute_subtotal',
        store=True,
    )

    @api.depends('price_unit', 'product_qty')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.price_unit * rec.product_qty

    def _prepare_purchase_order_line(
            self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super()._prepare_purchase_order_line(
            name, product_qty=product_qty, price_unit=0.0,
            taxes_ids=taxes_ids)
        if self.name:
            res.update({
                'name': self.name,
            })
        return res

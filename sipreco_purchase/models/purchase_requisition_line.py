##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    name = fields.Text(
        string='Description',
    )
    price_unit = fields.Float(
        string='Unit Price',
        digits=dp.get_precision('Product Price'),
    )
    subtotal = fields.Float(
        digits=dp.get_precision('Product Price'),
        compute='_compute_subtotal',
        store=True,
    )

    @api.depends('price_unit', 'product_qty')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.price_unit * rec.product_qty

    @api.multi
    def _prepare_purchase_order_line(
            self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super(
            PurchaseRequisitionLine, self)._prepare_purchase_order_line(
            name, product_qty=product_qty, price_unit=price_unit,
            taxes_ids=taxes_ids)
        if self.name:
            res.update({
                'name': self.name,
            })
        return res

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

    def get_comparative_order_line(self, purchase):
        """Return the line of ``purchase`` that quotes this requisition line.

        Used by the price comparison report. Lines are matched by product and,
        when the requisition repeats the product, also by description; equal
        lines are paired in order.
        """
        self.ensure_one()
        siblings = self.requisition_id.line_ids.filtered(
            lambda line: line.product_id == self.product_id)
        candidates = purchase.order_line.filtered(
            lambda line: line.product_id == self.product_id)
        if len(siblings) > 1:
            description = (self.name or '').strip()
            siblings = siblings.filtered(
                lambda line: (line.name or '').strip() == description)
            candidates = candidates.filtered(
                lambda line: (line.name or '').strip() == description)
        index = siblings.ids.index(self.id)
        return candidates[index] if index < len(candidates) else candidates.browse()

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

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
        res['requisition_line_id'] = self.id
        if self.name:
            res.update({
                'name': self.name,
            })
        return res

    @api.depends('requisition_id.line_ids', 'product_id', 'name')
    def _compute_display_name(self):
        for line in self:
            line_ids = line.requisition_id.line_ids.ids
            description = (line.name or '').strip().split('\n')[0]
            label = ' - '.join(filter(None, [line.product_id.display_name, description]))
            line.display_name = '%s. %s' % (line_ids.index(line.id) + 1, label) if line.id in line_ids else label

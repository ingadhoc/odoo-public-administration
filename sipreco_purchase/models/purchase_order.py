##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    expedient_id = fields.Many2one(
        'public_budget.expedient',
        copy=False,
    )

    user_confirmed_id = fields.Many2one(
        'res.users',
        readonly=True,
    )

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        super(PurchaseOrder, self)._onchange_requisition_id()
        if self.requisition_id.type_id.line_copy == 'copy'\
                and self.requisition_id.type_id.price_unit_copy != 'copy':
            self.order_line.update({'price_unit': 0.0})

    def check_if_expedients_exist(self):
        purchase_orders_expedient = self.filtered('expedient_id')
        if purchase_orders_expedient:
            raise UserError(
                _("This Purchase orders has expedient generated:\n * %s \n\n"
                    "Only one expedient for Purchase Order are allowed,"
                    " place select other Purchase orders.") %
                ("\n* ".join(
                    [p.name + '(%s)' % (p.expedient_id.number)
                     for p in purchase_orders_expedient])))

    @api.multi
    def button_confirm(self):
        super(PurchaseOrder, self).button_confirm()
        for rec in self.filtered(lambda x: x.state in ['to_approve', 'purchase']):
            rec.user_confirmed_id = self.env.user

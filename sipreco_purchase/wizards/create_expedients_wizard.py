from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PublicBudgetCreateExepedientsWizard(models.TransientModel):
    _name = "public_budget.create.expedients.wizard"
    _description = "public_budget.create.expedients.wizard"

    reference = fields.Char(
        required=False
    )
    founder_id = fields.Many2one(
        'public_budget.expedient_founder',
        required=True
    )
    category_id = fields.Many2one(
        'public_budget.expedient_category',
        required=True
    )
    first_location_id = fields.Many2one(
        'public_budget.location',
        required=True
    )
    user_location_ids = fields.Many2many(
        'public_budget.location',
        'public_budget_create_expedients_location_rel',
        default=lambda self: self.env.user.location_ids.ids,
    )
    pages = fields.Integer(
        required=True,
    )
    purchase_order_ids = fields.Many2many(
        'purchase.order',
        default=lambda self: self._default_purchase_orders(),
    )

    def _default_purchase_orders(self):
        purchase_order_ids = self._context.get('active_ids') or []
        purchase_orders = self.env['purchase.order'].browse(
            purchase_order_ids)
        return purchase_orders.ids

    def confirm(self):
        if not self.purchase_order_ids:
            raise UserError(_('It has no confirmed OC to generate '
                              'an expedient'))
        expedients = self.env['public_budget.expedient']
        for order in self.purchase_order_ids:
            vals = {
                'description': order.name,
                'supplier_ids': [(6, 0, [order.partner_id.id])],
                'reference': self.reference,
                'founder_id': self.founder_id.id,
                'category_id': self.category_id.id,
                'first_location_id': self.first_location_id.id,
                'pages': self.pages,
            }
            expedient = expedients.create(vals)
            # we do with sudo because in case that an user to only allow to read PO try to create an expedient
            # if came from an requisition.
            order.sudo().expedient_id = expedient.id
            expedients |= expedient
        action = self.env.ref(
            'public_budget.action_public_budget_expedient_expedients')
        action = action.read()[0]
        if not expedients or len(expedients) > 1:
            action['domain'] = "[('id','in',%s)]" % (expedients.ids)
        elif len(expedients) == 1:
            res = self.env.ref(
                'public_budget.view_public_budget_expedient_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = expedients.id
        return action

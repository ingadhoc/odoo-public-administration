from odoo import models, api


class BudgetTransaction(models.Model):

    _inherit = 'public_budget.transaction'

    @api.multi
    def action_view_purchase_requisitions(self):
        self.ensure_one()
        action = self.env.ref(
            'purchase_requisition.action_purchase_requisition')
        action = action.read()[0]
        action['context'] = {
            'search_default_expedient_id': self.expedient_id.id}
        return action

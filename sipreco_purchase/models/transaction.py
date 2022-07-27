from odoo import models


class BudgetTransaction(models.Model):

    _inherit = 'public_budget.transaction'

    def action_view_purchase_requisitions(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            'purchase_requisition.action_purchase_requisition')
        action['context'] = {'search_default_expedient_id': self.expedient_id.id}
        return action

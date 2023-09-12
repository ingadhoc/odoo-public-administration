from odoo import models, fields


class PublicBudgetExpedient(models.Model):

    _inherit = 'public_budget.expedient'

    purchase_order_ids = fields.One2many(
        'helpdesk.ticket',
        'expedient_id',
    )

    def action_open_subsidy_ticket(self):
        action = self.env["ir.actions.actions"]._for_xml_id("helpdesk.helpdesk_ticket_action_main_tree")
        action['context'] = {}
        all_child = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        action['domain'] = [('expedient_id', 'in', self.ids)]
        return action

from odoo import models, fields, api
# from odoo.exceptions import ValidationError


class PublicBudgetBudgetAnalysisWizard(models.TransientModel):
    _name = "public_budget.budget.analysis.wizard"

    budget_id = fields.Many2one(
        'public_budget.budget',
        'Presupuesto',
        required=True,
    )
    # from_date = fields.Date(
    #     'From Date',
    # )
    to_date = fields.Date(
        'Hasta Fecha',
    )

    @api.multi
    def confirm(self):
        self.ensure_one()
        actions = self.env.ref(
            'public_budget.action_position_analysis_tree')
        if not actions:
            return False
        action_read = actions.read()[0]
        # action_read['context'] = {
        #     'budget_id': self.budget_id.id,
        #     # 'analysis_from_date': self.from_date,
        #     'analysis_to_date': self.to_date,
        # }
        # return action_read
        actions = self.env.ref(
            'public_budget.action_public_budget_budget_budgets')
        if not actions:
            return False
        form_view = self.env.ref(
            'public_budget.view_public_budget_budget_to_date_form')
        action_read = actions.read()[0]
        action_read.pop('views')
        action_read['target'] = 'inlineview'
        action_read['res_id'] = self.budget_id.id
        action_read['view_mode'] = 'form'
        action_read['view_id'] = form_view.id,
        action_read['context'] = {
            # 'analysis_from_date': self.from_date,
            'analysis_to_date': self.to_date,
        }
        return action_read

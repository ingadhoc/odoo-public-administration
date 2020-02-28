from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PublicBudgetPreventiveChangePosition(models.TransientModel):
    _name = "public_budget.preventive.change_position"

    new_budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        required=True,
        ondelete='cascade',
        context={'default_type': 'normal'},
        domain=[('type', '=', 'normal')],
    )

    def confirm(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_model != 'public_budget.preventive_line' or not active_id:
            return False
        prev_line = self.env[active_model].browse(active_id)
        if prev_line.budget_id.state != 'open':
            raise ValidationError(_(
                'You can only change budget position if budget is open!'))
        prev_line.budget_position_id = self.new_budget_position_id.id

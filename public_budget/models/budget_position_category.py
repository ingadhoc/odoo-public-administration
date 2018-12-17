from odoo import models, fields


class BudgetPositionCategory(models.Model):
    """Budget Position Category"""

    _name = 'public_budget.budget_position_category'
    _description = 'Budget Position Category'

    name = fields.Char(
        required=True
    )

from odoo import models, fields


class BudgetPositionExchangeRestriction(models.Model):

    _name = 'public_budget.budget_pos_exc_rest'
    _description = 'Budget Position Exchange Restriction'

    origin_category_id = fields.Many2one(
        'public_budget.budget_position_category',
        required=True
    )
    destiny_category_id = fields.Many2one(
        'public_budget.budget_position_category',
        required=True
    )
    type = fields.Selection(
        [('alert', 'Alert'), ('block', 'Block')],
        required=True
    )
    message = fields.Char(
        required=True
    )

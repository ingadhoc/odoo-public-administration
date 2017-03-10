# -*- coding: utf-8 -*-
from openerp import models, fields, _


class BudgetDetail(models.Model):

    _name = 'public_budget.budget_detail'
    _description = 'Budget Detail'

    _order = "budget_position_id"

    initial_amount = fields.Monetary(
        string='Initial Amount',
        required=True,
    )
    state = fields.Selection(
        related='budget_id.state'
    )
    budget_id = fields.Many2one(
        'public_budget.budget',
        ondelete='cascade',
        string='budget_id',
        required=True
    )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        required=True,
        context={
            'default_type': 'normal', 'default_budget_assignment_allowed': 1},
        domain=[('budget_assignment_allowed', '=', True)]
    )
    currency_id = fields.Many2one(
        related='budget_id.currency_id',
        readonly=True,
    )

    _sql_constraints = [
        ('position_unique', 'unique(budget_position_id, budget_id)',
            _('Budget Position must be unique per Budget.'))]

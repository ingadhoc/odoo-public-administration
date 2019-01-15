from odoo import models, fields, api, _


class BudgetDetail(models.Model):

    _name = 'public_budget.budget_detail'
    _description = 'Budget Detail'

    _order = "budget_position_id"

    initial_amount = fields.Monetary(
        required=True,
    )
    state = fields.Selection(
        related='budget_id.state'
    )
    budget_id = fields.Many2one(
        'public_budget.budget',
        required=True
    )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        required=True,
        context={
            'default_type': 'normal', 'default_budget_assignment_allowed': 1},
        domain=[('budget_assignment_allowed', '=', True)]
    )
    currency_id = fields.Many2one(
        related='budget_id.currency_id',
        readonly=True,
    )
    amount = fields.Monetary(
        compute='_compute_amount',
    )
    modifications = fields.Monetary(
        compute='_compute_amount',
    )

    _sql_constraints = [
        ('position_unique', 'unique(budget_position_id, budget_id)',
            _('Budget Position must be unique per Budget.'))]

    @api.multi
    def _compute_amount(self):
        for rec in self:
            modifications = sum(
                rec.budget_id.budget_modification_ids.mapped(
                    'budget_modification_detail_ids').filtered(
                    lambda x: x.budget_position_id == rec.
                    budget_position_id).mapped('amount'))
            rec.update({
                'amount': rec.initial_amount + modifications,
                'modifications': modifications,
            })

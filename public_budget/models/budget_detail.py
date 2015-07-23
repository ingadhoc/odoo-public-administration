# -*- coding: utf-8 -*-
from openerp import models, fields, _
import openerp.addons.decimal_precision as dp


class budget_detail(models.Model):
    """"""

    _name = 'public_budget.budget_detail'
    _description = 'budget_detail'

    _order = "budget_position_id"

    initial_amount = fields.Float(
        string='Initial Amount',
        required=True,
        digits=dp.get_precision('Account'),
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

    _sql_constraints = [
        ('position_unique', 'unique(budget_position_id, budget_id)',
            _('Budget Position must be unique per Budget.'))]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

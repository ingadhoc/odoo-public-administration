# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class budget_modification_detail(models.Model):
    """Budget Modification Detail"""

    _name = 'public_budget.budget_modification_detail'
    _description = 'Budget Modification Detail'

    amount = fields.Float(
        string='Amount',
        required=True
        )
    budget_modification_id = fields.Many2one(
        'public_budget.budget_modification',
        ondelete='cascade',
        string='Modification',
        required=True
        )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        required=True,
        context={'default_type': 'normal', 'default_budget_assignment_allowed': 1},
        domain=[('budget_assignment_allowed', '=', True)]
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

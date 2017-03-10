# -*- coding: utf-8 -*-
from openerp import models, fields


class BudgetPositionExchangeRestriction(models.Model):

    _name = 'public_budget.budget_pos_exc_rest'
    _description = 'Budget Position Exchange Restriction'

    origin_category_id = fields.Many2one(
        'public_budget.budget_position_category',
        string='Origin Category',
        required=True
    )
    destiny_category_id = fields.Many2one(
        'public_budget.budget_position_category',
        string='Destiny Category',
        required=True
    )
    type = fields.Selection(
        [(u'alert', u'Alert'), (u'block', u'Block')],
        required=True
    )
    message = fields.Char(
        required=True
    )

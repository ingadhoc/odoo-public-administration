# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class budget_detail(models.Model):
    """"""

    _name = 'public_budget.budget_detail'
    _description = 'budget_detail'

    _order = "budget_position_id"

    initial_amount = fields.Float(
        string='Initial Amount',
        required=True
        )
    amount = fields.Float(
        string='Amount',
        compute='_get_amount'
        )
    draft_amount = fields.Float(
        string='Draft Amount',
        compute='_get_amounts'
        )
    preventive_amount = fields.Float(
        string='Preventive Amount',
        compute='_get_amounts'
        )
    definitive_amount = fields.Float(
        string='Definitive Amount',
        compute='_get_amounts'
        )
    to_pay_amount = fields.Float(
        string='To Pay Amount',
        compute='_get_amounts'
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        compute='_get_amounts'
        )
    balance_amount = fields.Float(
        string='Balance Amount',
        compute='_get_amounts'
        )
    state = fields.Selection(
        string='State',
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
        context={'default_type': 'normal', 'default_budget_assignment_allowed': 1},
        domain=[('budget_assignment_allowed', '=', True)]
        )

    _constraints = [
    ]

    @api.one
    def _get_amount(self):
        """"""
        raise NotImplementedError

    @api.one
    def _get_amounts(self):
        """"""
        raise NotImplementedError

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

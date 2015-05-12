# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class budget_prec_detail(models.Model):
    """"""

    _name = 'public_budget.budget_prec_detail'
    _description = 'Budget Preclose Detail'

    _order = "order_int"

    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        required=True
        )
    amount = fields.Float(
        string='Amount',
        readonly=True,
        required=True
        )
    draft_amount = fields.Float(
        string='Draft Amount',
        readonly=True,
        required=True
        )
    preventive_amount = fields.Float(
        string='Preventive Amount',
        readonly=True,
        required=True
        )
    definitive_amount = fields.Float(
        string='Definitive Amount',
        readonly=True,
        required=True
        )
    to_pay_amount = fields.Float(
        string='To Pay Amount',
        readonly=True,
        required=True
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        readonly=True,
        required=True
        )
    balance_amount = fields.Float(
        string='Balance Amount',
        readonly=True,
        required=True
        )
    account_type = fields.Selection(
        string='Type',
        related='budget_position_id.type'
        )
    order_int = fields.Integer(
        string='Parent Left'
        )
    budget_id = fields.Many2one(
        'public_budget.budget',
        ondelete='cascade',
        string='budget_id',
        required=True
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

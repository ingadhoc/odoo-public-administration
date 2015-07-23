# -*- coding: utf-8 -*-
from openerp import models, fields
import openerp.addons.decimal_precision as dp


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
        required=True,
        digits=dp.get_precision('Account'),
        )
    draft_amount = fields.Float(
        string='Draft Amount',
        readonly=True,
        required=True,
        digits=dp.get_precision('Account'),
        )
    preventive_amount = fields.Float(
        string='Preventive Amount',
        readonly=True,
        required=True,
        digits=dp.get_precision('Account'),
        )
    definitive_amount = fields.Float(
        string='Definitive Amount',
        readonly=True,
        required=True,
        digits=dp.get_precision('Account'),
        )
    to_pay_amount = fields.Float(
        string='To Pay Amount',
        readonly=True,
        required=True,
        digits=dp.get_precision('Account'),
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        readonly=True,
        required=True,
        digits=dp.get_precision('Account'),
        )
    balance_amount = fields.Float(
        string='Balance Amount',
        readonly=True,
        required=True,
        digits=dp.get_precision('Account'),
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

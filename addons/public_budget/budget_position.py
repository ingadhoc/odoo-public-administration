# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class budget_position(models.Model):
    """Budget Position"""

    _name = 'public_budget.budget_position'
    _description = 'Budget Position'

    _order = "parent_left"

    code = fields.Char(
        string='Code',
        required=True
        )
    name = fields.Char(
        string='Name',
        required=True
        )
    type = fields.Selection(
        [(u'normal', u'Normal'), (u'view', u'View')],
        string='Type',
        required=True,
        default='normal'
        )
    budget_assignment_allowed = fields.Boolean(
        string='Budget Assignment Allowed?'
        )
    category_id = fields.Many2one(
        'public_budget.budget_position_category',
        string='Category'
        )
    inventariable = fields.Boolean(
        string='Inventariable?'
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
    projected_amount = fields.Float(
        string='Projected Amount',
        compute='_get_amounts'
        )
    projected_avg = fields.Float(
        string='Projected Avg',
        compute='_get_amounts'
        )
    preventive_avg = fields.Float(
        string='Preventive Avg',
        compute='_get_amounts'
        )
    amount = fields.Float(
        string='Amount',
        compute='_get_amounts'
        )
    parent_left = fields.Integer(
        string='Parent Left',
        select=True
        )
    parent_right = fields.Integer(
        string='Parent Right',
        select=True
        )
    available_account_ids = fields.Many2many(
        'account.account',
        'public_budget_budget_position_ids_available_account_ids_rel',
        'budget_position_id',
        'account_id',
        string='Available Accounts'
        )
    child_ids = fields.One2many(
        'public_budget.budget_position',
        'parent_id',
        string='Childs'
        )
    parent_id = fields.Many2one(
        'public_budget.budget_position',
        string='Parent',
        ondelete='cascade',
        context={'default_type':'view'},
        domain=[('type','=','view')]
        )
    budget_detail_ids = fields.One2many(
        'public_budget.budget_detail',
        'budget_position_id',
        string='budget_detail_ids'
        )
    budget_modification_detail_ids = fields.One2many(
        'public_budget.budget_modification_detail',
        'budget_position_id',
        string='budget_modification_detail_ids'
        )
    preventive_line_ids = fields.One2many(
        'public_budget.preventive_line',
        'budget_position_id',
        string='preventive_line_ids'
        )

    _constraints = [
    ]

    @api.one
    def _get_amounts(self):
        """"""
        raise NotImplementedError

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

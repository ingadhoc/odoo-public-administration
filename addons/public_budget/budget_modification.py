# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class budget_modification(models.Model):
    """Budget Modification"""

    _name = 'public_budget.budget_modification'
    _description = 'Budget Modification'

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today
        )
    initial_approval = fields.Boolean(
        string='Is Initial Approval?'
        )
    type = fields.Selection(
        [(u'increase_decrease', u'Increase / Decrease'), (u'exchange', u'Exchange')],
        string='Budget Modification Type',
        required=True,
        default='increase_decrease'
        )
    name = fields.Char(
        string='Name',
        required=True
        )
    reference = fields.Char(
        string='Reference',
        required=True
        )
    rest_message = fields.Char(
        string='Message',
        compute='_get_restriction_data'
        )
    rest_type = fields.Many2one(
        'public_budget.rest_type',
        string='Restriction Type',
        compute='_get_restriction_data'
        )
    budget_id = fields.Many2one(
        'public_budget.budget',
        ondelete='cascade',
        string='Budget',
        required=True
        )
    budget_modification_detail_ids = fields.One2many(
        'public_budget.budget_modification_detail',
        'budget_modification_id',
        string='Details'
        )

    _constraints = [
    ]

    @api.one
    def _get_restriction_data(self):
        """"""
        raise NotImplementedError

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

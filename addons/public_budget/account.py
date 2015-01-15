# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class account(models.Model):
    """"""

    _name = 'account.account'
    _inherits = {}
    _inherit = ['account.account']

    budget_position_ids = fields.Many2many(
        'public_budget.budget_position',
        'public_budget_budget_position_ids_available_account_ids_rel',
        'account_id',
        'budget_position_id',
        string='budget_position_ids'
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

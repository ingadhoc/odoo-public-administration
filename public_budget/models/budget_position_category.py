# -*- coding: utf-8 -*-
from openerp import models, fields


class budget_position_category(models.Model):
    """Budget Position Category"""

    _name = 'public_budget.budget_position_category'
    _description = 'Budget Position Category'

    name = fields.Char(
        string='Name',
        required=True
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

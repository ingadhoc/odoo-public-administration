# -*- coding: utf-8 -*-
from openerp import models, fields


class budget_pos_exc_rest(models.Model):
    """Budget Position Exchange Restriction"""

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
        string='Type',
        required=True
    )
    message = fields.Char(
        string='Message',
        required=True
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

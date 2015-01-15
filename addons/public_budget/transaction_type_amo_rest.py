# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class transaction_type_amo_rest(models.Model):
    """Transaction Type Amount Restriction"""

    _name = 'public_budget.transaction_type_amo_rest'
    _description = 'Transaction Type Amount Restriction'

    _order = "date desc"

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today
        )
    from_amount = fields.Float(
        string='From Amount',
        required=True
        )
    to_amount = fields.Float(
        string='To Amount',
        required=True
        )
    transaction_type_id = fields.Many2one(
        'public_budget.transaction_type',
        ondelete='cascade',
        string='transaction_type_id',
        required=True
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
from openerp import models, fields
import openerp.addons.decimal_precision as dp


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
        required=True,
        digits=dp.get_precision('Account'),
    )
    to_amount = fields.Float(
        string='To Amount',
        required=True,
        digits=dp.get_precision('Account'),
    )
    transaction_type_id = fields.Many2one(
        'public_budget.transaction_type',
        ondelete='cascade',
        string='transaction_type_id',
        required=True
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

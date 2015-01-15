# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class voucher(models.Model):
    """"""

    _name = 'account.voucher'
    _inherits = {}
    _inherit = ['account.voucher']

    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transaction',
        readonly=True
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

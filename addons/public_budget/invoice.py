# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class invoice(models.Model):
    """"""

    _name = 'account.invoice'
    _inherits = {}
    _inherit = ['account.invoice']

    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='transaction_id'
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

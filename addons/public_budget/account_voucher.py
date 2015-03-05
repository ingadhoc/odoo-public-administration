# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class account_voucher(models.Model):
    """"""

    _name = 'account.voucher'
    _inherits = {}
    _inherit = ['account.voucher']

    type_with_advance_payment = fields.Boolean(
        string='With advance payment?',
        readonly=True,
        related='transaction_id.type_id.with_advance_payment'
        )
    note = fields.Html(
        string='Note'
        )
    paid = fields.Boolean(
        string='Paid',
        compute='_get_paid'
        )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transaction'
        )

    _constraints = [
    ]

    @api.one
    def _get_paid(self):
        """"""
        parent = super(account_voucher,self)
        result = parent._get_paid() if hasattr(parent, '_get_paid') else False
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

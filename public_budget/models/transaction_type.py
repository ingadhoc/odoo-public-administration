# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class transaction_type(models.Model):
    """Transaction Type"""

    _name = 'public_budget.transaction_type'
    _description = 'Transaction Type'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
    )
    with_amount_restriction = fields.Boolean(
        string='With Amount Restriction?'
    )
    with_advance_payment = fields.Boolean(
        string='With advance payment?'
    )
    advance_account_id = fields.Many2one(
        'account.account',
        string='Advance Account',
        context={'default_type': 'other'},
        # we use receivable to get debt but we dont reconcile
        domain="[('type', 'in', ['receivable']), ('reconcile', '=', False), "
        "('company_id', '=', company_id)]",
        help='This account will be used on advance payments. Must be a payable'
        ' account.',
    )
    amount_restriction_ids = fields.One2many(
        'public_budget.transaction_type_amo_rest',
        'transaction_type_id',
        string='Amount Restrictions'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id,
    )

    @api.one
    @api.constrains('advance_account_id', 'company_id')
    def check_account_company(self):
        if (
                self.advance_account_id and
                self.advance_account_id.company_id != self.company_id
        ):
            raise Warning(_(
                'Company must be the same as Account Company!'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

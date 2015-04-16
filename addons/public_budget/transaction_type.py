# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


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
    with_salary_advance = fields.Boolean(
        string='With Advance Salary'
        )
    with_advance_payment = fields.Boolean(
        string='With advance payment?'
        )
    advance_account_id = fields.Many2one(
        'account.account',
        string='Advance Account',
        context={'default_type': 'other'},
        # we use payable accounts because we need them in vouchers of type payment
        domain=[('type', 'in', ('payable'))],
        help='This account will be used on advance payments. Must be a payable account.',
        # domain=[('type', '=', 'other'), ('user_type.report_type', 'in', ['asset'])],
        )
    advance_journal_id = fields.Many2one(
        'account.journal',
        string='Advance Journal',
        context={'default_type': 'cash', 'default_allow_direct_payment': True},
        domain=[
            ('type', 'in', ('cash', 'bank')),
            ('allow_direct_payment', '=', True)],
        help='This journal balance advance payments and supplier invoices',
        )
    amount_restriction_ids = fields.One2many(
        'public_budget.transaction_type_amo_rest',
        'transaction_type_id',
        string='Amount Restrictions'
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

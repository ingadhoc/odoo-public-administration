from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransactionType(models.Model):
    """Transaction Type"""

    _name = 'public_budget.transaction_type'
    _description = 'Transaction Type'
    _check_company_auto = True

    name = fields.Char(
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
        domain=[('deprecated', '=', False), ('reconcile', '=', False), ('account_type', 'not in', ['asset_cash', 'liability_credit_card'])],
        help='This account will be used on advance payments',
        check_company=True,
    )
    amount_restriction_ids = fields.One2many(
        'public_budget.transaction_type_amo_rest',
        'transaction_type_id',
        string='Amount Restrictions'
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    definitive_partner_type = fields.Selection([
        ('supplier', 'Suppliers'),
        ('subsidy_recipient', 'Subsidy Recipients'),
    ],
        'Definitive Partner Type',
        default='supplier',
        required=True,
    )

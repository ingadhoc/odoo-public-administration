from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransactionType(models.Model):
    """Transaction Type"""

    _name = 'public_budget.transaction_type'
    _description = 'Transaction Type'

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
        domain="[('company_id', '=', company_id), "
        "('internal_type', '=', 'liquidity'), ('deprecated', '=', False)]",
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
    definitive_partner_type = fields.Selection([
        ('supplier', 'Suppliers'),
        ('subsidy_recipient', 'Subsidy Recipients'),
    ],
        'Definitive Partner Type',
        default='supplier',
        required=True,
    )

    @api.constrains('advance_account_id', 'company_id')
    def check_account_company(self):
        for rec in self:
            if (
                    rec.advance_account_id and
                    rec.advance_account_id.company_id != rec.company_id
            ):
                raise ValidationError(_(
                    'Company must be the same as Account Company!'))

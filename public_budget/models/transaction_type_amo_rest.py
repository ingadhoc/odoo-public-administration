# -*- coding: utf-8 -*-
from odoo import models, fields


class TransactionTypeAmountRestriction(models.Model):
    """Transaction Type Amount Restriction"""

    _name = 'public_budget.transaction_type_amo_rest'
    _description = 'Transaction Type Amount Restriction'

    _order = "date desc"

    date = fields.Date(
        required=True,
        default=fields.Date.context_today
    )
    from_amount = fields.Monetary(
        required=True,
    )
    to_amount = fields.Monetary(
        required=True,
    )
    transaction_type_id = fields.Many2one(
        'public_budget.transaction_type',
        ondelete='cascade',
        string='transaction_type_id',
        required=True
    )
    currency_id = fields.Many2one(
        related='transaction_type_id.company_id.currency_id',
        readonly=True,
    )

# -*- coding: utf-8 -*-
from openerp import models, fields


class transaction_type(models.Model):
    """Transaction Type"""

    _inherit = 'public_budget.transaction_type'

    _partner_types_ = [
        ('supplier', 'Suppliers'),
        ('subsidy_recipient', 'Subsidy Recipients'),
    ]

    definitive_partner_type = fields.Selection(
        _partner_types_,
        'Definitive Partner Type',
        default='supplier',
        required=True,
        )

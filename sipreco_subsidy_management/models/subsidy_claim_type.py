# -*- coding: utf-8 -*-
from openerp import fields, models
import logging
_logger = logging.getLogger(__name__)


class PublicBudgetSubsidyClaimType(models.Model):

    _name = 'public_budget.subsidy.claim.type'
    _order = 'sequence'

    sequence = fields.Integer(
        required=True,
        default=10,
    )
    name = fields.Char(
        required=True,
    )
    code = fields.Char(
        required=True,
    )

# -*- coding: utf-8 -*-
from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)


class PublicBudgetTransactionType(models.Model):

    _inherit = 'public_budget.transaction_type'

    subsidy = fields.Boolean(
    )

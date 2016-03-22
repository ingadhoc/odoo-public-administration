# -*- coding: utf-8 -*-
from openerp import fields, models
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class PublicBudgetSubsidyRendition(models.Model):

    _name = 'public_budget.subsidy.rendition'

    subsidy_id = fields.Many2one(
        'public_budget.subsidy',
        'Subsidy',
        required=True,
        ondelete='cascade',
        )
    name = fields.Char(
        required=True,
        )
    date = fields.Date(
        required=True,
        default=fields.Date.context_today
        )
    rendition_amount = fields.Float(
        'Monto Rendido',
        digits=dp.get_precision('Account'),
        )
    approved_amount = fields.Float(
        'Monto Aprobado',
        digits=dp.get_precision('Account'),
        )

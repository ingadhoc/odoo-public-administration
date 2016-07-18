# -*- coding: utf-8 -*-
from openerp import fields, models, api
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
    date = fields.Date(
        required=True,
        default=fields.Date.context_today
    )
    approval_arrangement_ids = fields.Many2many(
        'public_budget.approval_arrangement',
        'public_budget_rendition_approval_arrangement_rel',
        'rendition_id', 'approval_arrangement_id',
        'Disposiciones de aprobación',
    )
    rendition_amount = fields.Float(
        'Monto Rendido',
        digits=dp.get_precision('Account'),
    )
    approved_amount = fields.Float(
        'Monto Aprobado',
        digits=dp.get_precision('Account'),
    )
    pending_amount = fields.Float(
        'Monto Pendiente',
        digits=dp.get_precision('Account'),
        compute='get_pending_amount',
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        'Expediente',
        help='Expediente Administrativo de Rendición de Subsidio',
    )

    @api.one
    @api.depends('rendition_amount', 'approved_amount')
    def get_pending_amount(self):
        self.pending_amount = self.rendition_amount - self.approved_amount

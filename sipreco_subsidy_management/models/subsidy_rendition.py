# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.exceptions import Warning
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
    # approval_arrangement_ids = fields.One2many(
    #     'public_budget.subsidy.approval_arrangement',
    #     'rendition_id',
    #     # 'public_budget_rendition_approval_arrangement_rel',
    #     # 'rendition_id', 'approval_arrangement_id',
    #     'Disposiciones de aprobación',
    # )
    approval_arrangement_id = fields.Many2one(
        'public_budget.subsidy.approval_arrangement',
        # 'rendition_id',
        # 'public_budget_rendition_approval_arrangement_rel',
        # 'rendition_id', 'approval_arrangement_id',
        'Disposición de aprobación',
    )
    rendition_amount = fields.Float(
        'Importe Rendido',
        digits=dp.get_precision('Account'),
    )
    approved_amount = fields.Float(
        'Importe Aprobado',
        related='approval_arrangement_id.approved_amount',
        readonly=True,
        store=True,
        # digits=dp.get_precision('Account'),
    )
    pending_amount = fields.Float(
        'Importe Pendiente',
        digits=dp.get_precision('Account'),
        compute='get_pending_amount',
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        'Expediente',
        help='Expediente Administrativo de Rendición de Subsidio',
    )
    editable_line = fields.Boolean(
        'Block editing line',
        default=False)

    @api.one
    @api.constrains('rendition_amount', 'approved_amount')
    def check_amounts(self):
        if self.approved_amount > self.rendition_amount:
            raise Warning(
                'Importe Aprobado no puede ser mayor al importe rendido')

    @api.one
    @api.depends('rendition_amount', 'approved_amount')
    def get_pending_amount(self):
        self.pending_amount = self.rendition_amount - self.approved_amount

    @api.multi
    def unlink(self):
        for record in self:
            if record.approval_arrangement_id and record.editable_line:
                raise Warning(
                    'No es posible borrar una rendición'
                    ' que presente montos Aprobados')
            else:
                return super(PublicBudgetSubsidyRendition, self).unlink()

    @api.one
    @api.constrains('approval_arrangement_id')
    def on_change_approval_arrangement_id(self):
        if self.approval_arrangement_id:
            self.editable_line = True

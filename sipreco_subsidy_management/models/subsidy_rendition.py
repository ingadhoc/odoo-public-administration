from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class PublicBudgetSubsidyRendition(models.Model):

    _name = 'public_budget.subsidy.rendition'
    _description = 'public_budget.subsidy.rendition'

    subsidy_id = fields.Many2one(
        'public_budget.subsidy',
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
    rendition_amount = fields.Monetary(
        'Importe Rendido',
    )
    currency_id = fields.Many2one(
        related='subsidy_id.currency_id'
    )
    approved_amount = fields.Monetary(
        'Importe Aprobado',
        related='approval_arrangement_id.approved_amount',
        store=True,
    )
    pending_amount = fields.Monetary(
        'Importe Pendiente',
        compute='_compute_pending_amount',
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        'Expediente',
        help='Expediente Administrativo de Rendición de Subsidio',
        ondelete='restrict',
    )
    editable_line = fields.Boolean(
        'Block editing line',
        default=False)

    @api.constrains('rendition_amount', 'approved_amount')
    def check_amounts(self):
        if self.filtered(
                lambda x: x.approved_amount > x.rendition_amount):
            raise ValidationError(_(
                'Importe Aprobado no puede ser mayor al importe rendido'))

    @api.depends('rendition_amount', 'approved_amount')
    def _compute_pending_amount(self):
        self.pending_amount = self.rendition_amount - self.approved_amount

    def unlink(self):
        if self.filtered(lambda x: x.approval_arrangement_id and x.editable_line):
            raise UserError(_(
                    'No es posible borrar una rendición'
                    ' que presente montos Aprobados'))
        return super().unlink()

    @api.constrains('approval_arrangement_id')
    def on_change_approval_arrangement_id(self):
        self.filtered('approval_arrangement_id').write({'editable_line': True})

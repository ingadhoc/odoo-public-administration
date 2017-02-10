# -*- coding: utf-8 -*-
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class ApprovalArrangement(models.Model):

    _name = 'public_budget.subsidy.approval_arrangement'
    _rec_name = 'number'

    # @api.model
    # def _get_approved_amount(self):
    #     # lo hacemos asi porque mandando por vista nos daba error
    #     rendition_id = self._context.get('default_rendition_id')
    #     if rendition_id:
    #         return self.env['public_budget.subsidy.rendition'].browse(
    #             rendition_id).rendition_amount
    #     return False

    @api.model
    def create(self, vals):
        if not vals.get('number'):
            vals['number'] = self.env['ir.sequence'].get(
                'approval_arrangement')
        return super(ApprovalArrangement, self).create(vals)

    number = fields.Char(
        required=True,
        readonly=True,
        # default=_get_number,
    )
    fojas = fields.Integer(
        required=True,
    )
    rendition_ids = fields.One2many(
        'public_budget.subsidy.rendition',
        'approval_arrangement_id',
        'Rendición',
        # required=True,
    )
    # rendition_id = fields.Many2one(
    #     'public_budget.subsidy.rendition',
    #     'Rendición',
    #     required=True,
    # )
    # subsidy_id = fields.Many2one(
    #     'public_budget.subsidy',
    #     'Subsidio',
    #     required=True,
    # )
    approved_amount = fields.Float(
        'Monto Aprobado',
        required=True,
        digits=dp.get_precision('Account'),
        # default=_get_approved_amount,
    )

    _sql_constraints = [
        ('number_unique', 'unique(number)',
            ('El número debe ser único en las disposiciones de aprobación'))]

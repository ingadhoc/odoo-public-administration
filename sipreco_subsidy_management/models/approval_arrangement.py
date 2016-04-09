# -*- coding: utf-8 -*-
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class ApprovalArrangement(models.Model):

    _name = 'public_budget.approval_arrangement'
    _rec_name = 'number'

    # @api.model
    # def _get_number(self):
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
    subsidy_id = fields.Many2one(
        'public_budget.subsidy',
        'Subsidio',
        required=True,
        )
    approved_amount = fields.Float(
        'Monto Aprobado',
        digits=dp.get_precision('Account'),
        )
    description = fields.Text(
        'Texto Adicional'
        )

    _sql_constraints = [
        ('number_unique', 'unique(number)',
            ('El número debe ser único en las disposiciones de aprobación'))]
# Nro (secuencial nro y año, 0001/16)
# Se reinciian año a año
# Subisidio
# Monto Aprobado
# Texto adicional (para incrustar en reporte de word)
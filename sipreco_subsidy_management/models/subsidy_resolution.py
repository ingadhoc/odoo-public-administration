# -*- coding: utf-8 -*-
from openerp import fields, models, api


class PublicBudgetSubsidyResolution(models.Model):

    _name = 'public_budget.subsidy.resolution'

    name = fields.Char(
        'Nombre',
        required=True
    )
    date = fields.Date(
        string='Fecha de la Resolucion',
        required=True
    )
    reference = fields.Char(
        'Referencia',
        required=True,
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expediente',
        required=True,
    )
    state = fields.Selection([
        ('not_presented', 'No Presentado'),
        ('presented', 'Presentado')],
        'Estado',
        default='not_presented'
    )
    subsidy_resolution_line_ids = fields.One2many(
        'public_budget.subsidy.resolution.line',
        'subsidy_resolution_id'
    )

    @api.multi
    def action_change_state(self):
        for rec in self:
            if rec.state == 'not_presented':
                rec.state = 'presented'
            elif rec.state == 'presented':
                rec.state = 'not_presented'


class PublicBudgetSubsidyResolutionLines(models.Model):

    _name = 'public_budget.subsidy.resolution.line'

    name = fields.Char(
        'Nombre de Receptor',
        required=True
    )
    dni = fields.Integer(
        'DNI de Receptor',
        required=True
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expediente',
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Concejal',
        domain=[('employee', '=', True)],
        required=True,
    )
    amount = fields.Integer(
        'Monto',
        required=True,
    )
    subsidy_resolution_id = fields.Many2one(
        'public_budget.subsidy.resolution'
    )

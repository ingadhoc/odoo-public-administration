# -*- coding: utf-8 -*-
from openerp import fields, models, api


class PublicBudgetSubsidyResolution(models.Model):

    _name = 'public_budget.subsidy.resolution'

    name = fields.Char(
        'Nombre',
        required=True
    )
    date = fields.Date(
        'Fecha de la Resolucion',
        required=True
    )
    reference = fields.Char(
        'Referencia',
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

    current_location_id = fields.Many2one(
        'public_budget.location',
        string='Ubicación Actual',
        required=True,
    )

    @api.multi
    def action_change_state(self):
        for rec in self:
            if rec.state == 'not_presented':
                rec.state = 'presented'
            elif rec.state == 'presented':
                rec.state = 'not_presented'

    @api.constrains('state')
    def _validate_state_presented(self):
        for rec in self:
            if rec.state == 'presented':
                for exp in rec.mapped(
                        'subsidy_resolution_line_ids.expedient_id'):
                    exp.subsidy_approved = True


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
        required=True,
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

    _sql_constraints = [
        ('dni', 'unique(dni, subsidy_resolution_id)',
         '¡DNI duplicado en las lineas! Revisar'),
        ('expedient_id', 'unique(expedient_id, subsidy_resolution_id)',
                         '¡Expediente Duplicado! Revisar')]

    @api.onchange('expedient_id')
    def _onchange_expedient_id(self):
        self.partner_id = self.expedient_id.employee_subsidy_requestor
        self.name = self.expedient_id.cover
        self.dni = self.expedient_id.subsidy_recipient_doc

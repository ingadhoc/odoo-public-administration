# -*- coding: utf-8 -*-
from openerp import fields, models, api


class PublicBudgetSubsidyResolution(models.Model):

    _name = 'public_budget.subsidy.resolution'

    name = fields.Char(
        'Name',
        required=True
    )
    date = fields.Date(
        'Date of resolution',
        required=True
    )
    reference = fields.Char(
        'Reference',
        required=True,
    )
    state = fields.Selection([
        ('not_presented', 'Not Presented'),
        ('presented', 'Presented')],
        'State',
        default='not_presented'
    )
    subsidy_resolution_line_ids = fields.One2many(
        'public_budget.subsidy.resolution.line',
        'subsidy_resolution_id'
    )

    current_location_id = fields.Many2one(
        'public_budget.location',
        string='Current Location',
        required=True,
    )
    location_dest_id = fields.Many2one(
        'public_budget.location',
        string='Destination Location',
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user
    )
    user_location_ids = fields.Many2many(
        related='user_id.location_ids',
        readonly=True,
    )

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        """
        Idea obtenida de aca
        https://github.com/odoo/odoo/issues/16072#issuecomment-289833419
        por el cambio que se introdujo en esa mimsa conversación, TODO en v11
        no haría mas falta, simplemente domain="[('id', 'in', x2m_field)]"
        Otras posibilidades que probamos pero no resultaron del todo fue:
        * agregar onchange sobre campos calculados y que devuelvan un dict con
        domain. El tema es que si se entra a un registro guardado el onchange
        no se ejecuta
        * usae el modulo de web_domain_field que esta en un pr a la oca
        """
        for field in field_onchange.keys():
            if field.startswith('user_location_ids.'):
                del field_onchange[field]
        return super(PublicBudgetSubsidyResolution, self).onchange(
            values, field_name, field_onchange)

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
                rec.mapped('subsidy_resolution_line_ids.expedient_id').write(
                    {'subsidy_approved': True})

    @api.multi
    def generate_remit(self):
        vals = {
            'location_id': self.current_location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'reference': self.reference,
        }
        remit = self.env['public_budget.remit'].create(vals)
        remit.expedient_ids = self.mapped(
            'subsidy_resolution_line_ids.expedient_id').ids
        action_read = False
        actions = self.env.ref(
            'public_budget.action_public_budget_remit_remits')
        if actions:
            action_read = actions.read()[0]
            action_read['name'] = 'Remitos'
            action_read['domain'] = [('id', '=', remit.id)]
        return action_read


class PublicBudgetSubsidyResolutionLines(models.Model):

    _name = 'public_budget.subsidy.resolution.line'

    name = fields.Char(
        'Name of Receiver',
        required=True
    )
    dni = fields.Integer(
        'DNI of Receiver',
        required=True
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expedient',
        required=True,
        domain="['|',('state', 'not in' , ['cancel', 'annulled'])"
        ",('defeated' ,'!=', True)]"
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Councilor',
        domain=[('employee', '=', True)],
        required=True,
    )
    amount = fields.Integer(
        'Amount',
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

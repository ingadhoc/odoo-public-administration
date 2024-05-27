from odoo import fields, models, api, _
import odoo.http as http
from odoo.exceptions import ValidationError, UserError
import stdnum

class PublicBudgetSubsidyTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    dni = fields.Char(
        size=11,
        string="DNI",
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True,
    )
    amount = fields.Integer(
    )
    cbu = fields.Char(
        size=22,
        string="CBU",
    )
    photo_dni = fields.Binary(
        string="Foto DNI",
        store=True,
    )
    expedient_id = fields.Many2one(
        "public_budget.expedient",
        string="Tramite Administrativo",
        copy=False,
        readonly=True,
    )
    issue_date = fields.Datetime(
        compute='_compute_issue_date',
        string="Fecha del TA",
        copy=False,
        readonly=True,
    )
    responsible_user = fields.Many2one(
        'res.users',
        string="Usuario Responsable",
    )
    resolution_number = fields.Char(
        string="Número de Resolución",
    )
    resolution_date = fields.Date(
        string="Fecha de Resolución",
    )

    @api.model
    def create(self, values):
        dni = values.get('dni')
        if (dni and len(dni) != 8) and (dni and len(dni) != 11):
                raise ValidationError("El DNI debe tener 8 caracteres y el CUIT 11 caracteres")
        cbu = values.get('cbu')
        if cbu and len(cbu) != 22:
                raise ValidationError("El CBU debe tener 22 caracteres.")
        partner = self.env['res.partner'].search([('vat', '=', dni)], limit=1)
        if partner:
            values['partner_id'] = partner.id
            values['partner_name'] = partner.name
            values['partner_phone'] = partner.phone
            values['partner_email'] = partner.email

        ticket = super(PublicBudgetSubsidyTicket, self).create(values)
        user = http.request.env.user
        if user:
            ticket.responsible_user = user
        if ticket.dni and ticket.partner_id:
            partner = ticket.partner_id
            partner.subsidy_recipient = True
            if len(ticket.dni) == 8:
                dni_identification_type = self.env['l10n_latam.identification.type'].search([('name', '=', 'DNI')], limit=1)
            if len(ticket.dni) == 11:
                dni_identification_type = self.env['l10n_latam.identification.type'].search([('name', '=', 'CUIT')], limit=1)
            if dni_identification_type:
                partner.l10n_latam_identification_type_id = dni_identification_type.id
            partner.vat = ticket.dni
        elif not ticket.partner_id and len(ticket.dni) == 8:
            partner = self.env['res.partner'].create({
                'name': ticket.partner_name,
                'mobile': ticket.partner_phone,
                'l10n_latam_identification_type_id': self.env['l10n_latam.identification.type'].search([('name', '=', 'DNI')], limit=1).id,
                'l10n_ar_afip_responsibility_type_id': self.env['l10n_ar.afip.responsibility.type'].search([('name', '=', 'Consumidor Final')], limit=1).id,
                'vat': ticket.dni,
                'subsidy_recipient': True,
            })
            ticket.partner_id = partner.id
        elif not ticket.partner_id and len(ticket.dni) == 11:
            partner = self.env['res.partner'].create({
                'name': ticket.partner_name,
                'mobile': ticket.partner_phone,
                'l10n_latam_identification_type_id': self.env['l10n_latam.identification.type'].search([('name', '=', 'CUIT')], limit=1).id,
                'l10n_ar_afip_responsibility_type_id': self.env['l10n_ar.afip.responsibility.type'].search([('name', '=', 'Consumidor Final')], limit=1).id,
                'vat': ticket.dni,
                'subsidy_recipient': True,
            })
            ticket.partner_id = partner.id
        return ticket

    def _compute_issue_date(self):
        for ticket in self:
            if ticket.expedient_id:
                ticket.issue_date = ticket.expedient_id.issue_date
            else:
                ticket.issue_date = False

    @api.model
    def name_get(self):
        result = []
        for ticket in self:
            year = ticket.create_date.year
            name_with_year = "%s (#%d) - %d" % (ticket.name, ticket._origin.id, year)
            result.append((ticket.id, name_with_year))
        return result

    @api.constrains('stage_id')
    def _check_expedient(self):
        ''' Check if tickets has an expedient associated in order to change to the expedient stage '''
        if not self.expedient_id and self.stage_id.name == "Tramite Administrativo":
            raise UserError(_('El ticket debe tener un tramite administrativo asociado para pasarlo a esta etapa'))
        if self.expedient_id and self.stage_id.name != "Tramite Administrativo":
            raise UserError(_('El ticket tiene un tramite administrativo asociado, por lo tanto no puede retroceder una etapa'))

    @api.constrains('stage_id')
    def _check_stage_id(self):
        tickets_duplicados = []
        for rec in self: 
            if rec.stage_id.is_verified:
                duplicado = self.search([('stage_id', '=',rec.stage_id.id ),('id', '!=', rec.id),('dni', '=', rec.dni)],limit = 1)                
                if duplicado:
                    tickets_duplicados.append(duplicado.dni)
        if tickets_duplicados:
            dnis_unicos = set(tickets_duplicados)
            string = ", ".join(dnis_unicos)
            raise ValidationError('El/los Dni/s %s tienen solicitudes duplicadas' % string)

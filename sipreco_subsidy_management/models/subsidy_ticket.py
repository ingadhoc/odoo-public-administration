from odoo import fields, models, api, _
import odoo.http as http
from odoo.exceptions import ValidationError
import stdnum

class PublicBudgetSubsidyTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    dni = fields.Char(
        size=8,
        string="DNI",
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True,
    )
    amount = fields.Monetary(
        currency_field='currency_id',
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
        readonly=True,
    )
    resolution_number = fields.Char(
        string="Número de Resolución",
    )
    resolution_date = fields.Date(
        string="Fecha de Resolución",
    )

    @api.constrains('cbu')
    def _check_cbu_length(self):
        for partner in self:
            if partner.cbu and len(partner.cbu) != 22:
                raise ValidationError("El CBU debe tener 22 caracteres.")

    @api.constrains('dni')
    def _check_dni_length(self):
        for partner in self:
            if partner.dni and len(partner.dni) != 8:
                raise ValidationError("El DNI debe tener 8 caracteres.")

    @api.model
    def create(self, values):
        ticket = super(PublicBudgetSubsidyTicket, self).create(values)

        user = http.request.env.user
        if user:
            ticket.responsible_user = user
        if ticket.dni and ticket.partner_id:
            partner = ticket.partner_id
            dni_identification_type = self.env['l10n_latam.identification.type'].search([('name', '=', 'DNI')], limit=1)
            if dni_identification_type:
                partner.l10n_latam_identification_type_id = dni_identification_type.id
            partner.vat = ticket.dni
        return ticket

    def _compute_issue_date(self):
        if self.expedient_id:
            self.issue_date = self.expedient_id.issue_date
        else:
            self.issue_date = False

from odoo import fields, models, api, _
import odoo.http as http
from odoo.exceptions import ValidationError
import stdnum

class PublicBudgetSubsidyTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    dni = fields.Char(
        size=8,
        string="DNI",
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True,
    )
    amount = fields.Monetary(
        required=True,
        currency_field='currency_id',
    )
    cbu = fields.Char(
        size=22,
        string="CBU",
        required=True,
    )
    photo_dni = fields.Binary(
        string="Foto DNI",
        store=True,
    )
    expedient_id = fields.Many2one(
        "public_budget.expedient",
        string="Expediente",
        copy=False,
        readonly=True,
    )
    responsible_user = fields.Many2one(
        'res.users',
        string="Usuario Responsable",
        readonly=True,
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

    # def action_view_ticket(self):
    #     self.ensure_one()
    #     action =  self.env["ir.actions.act_window"]._for_xml_id(
    #         'sipreco_subsidy_management.action_sipreco_subsidy_management_subsidy_tickets')
    #     action['domain'] = [('id', 'in', self.ticket_ids.ids)]
    #     return action

    @api.model_create_multi
    def create(self, list_value):
        tickets = super().create(list_value)
        for ticket in tickets:
            user = http.request.env.user
            if user:
                ticket.responsible_user = user
        return tickets

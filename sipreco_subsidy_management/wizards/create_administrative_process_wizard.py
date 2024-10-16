from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError


class PublicBudgetCreateAdministrativeProcessWizard(models.TransientModel):
    _name = "public_budget.create.administrative.process.wizard"
    _description = "public_budget.create.administrative.process.wizard"

    reference = fields.Char(
        required=False
    )
    founder_id = fields.Many2one(
        'public_budget.expedient_founder',
        required=True
    )
    category_id = fields.Many2one(
        'public_budget.expedient_category',
        required=True
    )
    first_location_id = fields.Many2one(
        'public_budget.location',
        required=True,
    )
    user_location_ids = fields.Many2many(
        'public_budget.location',
        'public_budget_create_administrative_process_location_rel',
        default=lambda self: self.env.user.location_ids.ids,
    )
    pages = fields.Integer(
        required=True,
    )
    helpdesk_ticket_ids = fields.Many2one(
        'helpdesk.ticket',
    )

    def confirm(self):
        active_tickets_ids = self._context.get('active_ids') or []
        tickets = self.env['helpdesk.ticket'].browse(active_tickets_ids)
        if tickets and tickets.expedient_id:
            raise UserError(_('Uno de los tickets ya tiene un expediente asociado'))
        if not tickets:
            raise UserError(_('Los tickets deben estar aprobados para poder generar un expediente'))
        if len(set(tickets.mapped('dni'))) != len(tickets.mapped('dni')):
            raise UserError('No puede haber varios tickets con el mismo DNI en el mismo expediente.')
        vals = {
            'description': tickets[0].name,
            'supplier_ids': [Command.set(tickets.partner_id.ids)],
            'reference': self.reference,
            'founder_id': self.founder_id.id,
            'category_id': self.category_id.id,
            'first_location_id': self.first_location_id.id,
            'pages': self.pages,
        }

        expedient = self.env['public_budget.expedient'].create(vals)
        tickets.write({'expedient_id': expedient.id})
        stage = self.env['helpdesk.stage'].search([('name', '=', "Tramite Administrativo")], limit=1)
        tickets.write({'stage_id': stage.id})

        action = self.env["ir.actions.actions"]._for_xml_id(
            'public_budget.action_public_budget_expedient_expedients')

        if expedient:
            res = self.env.ref('public_budget.view_public_budget_expedient_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = expedient.id
        return action

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PublicBudgetSubsidyResolution(models.Model):

    _name = 'public_budget.subsidy.resolution'
    _description = 'public_budget.subsidy.resolution'
    _order = 'date desc'

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
    )

    def action_change_state(self):
        for rec in self:
            if rec.state == 'not_presented':
                rec.state = 'presented'
            elif rec.state == 'presented':
                rec.state = 'not_presented'

    @api.constrains('state')
    def _validate_state_presented(self):
        for rec in self.filtered(lambda x: x.state == 'presented'):
            rec.mapped('subsidy_resolution_line_ids.expedient_id').write(
                {'subsidy_approved': True})

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

    @api.constrains('state')
    def check_state(self):
        for rec in self.filtered(lambda x: x.state == 'presented'):
            six_months_ago = fields.Date.subtract(rec.date, months=6)
            msj = ""
            for sub_res in rec.subsidy_resolution_line_ids:
                domain = [
                    ('dni', '=', sub_res.dni),
                    ('subsidy_resolution_id.date', '>', six_months_ago),
                    ('subsidy_resolution_id.state', '=', 'presented')]
                resolutions_with_expedient = rec.subsidy_resolution_line_ids.search(
                    domain)
                resolutions_with_expedient -= sub_res
                if len(resolutions_with_expedient) > 0:
                    msj += "- {} \n".format("Name: {}  DNI: {} \n {}".format(
                        sub_res.name, sub_res.dni, " * " + "\n * ".join(
                            resolutions_with_expedient.mapped(lambda x: " - ".join(
                                [str(x.subsidy_resolution_id.date),
                                 x.subsidy_resolution_id.name])))))
            if msj:
                raise ValidationError(
                    _('There is the same beneficiary in resolutions within 180 days'
                      ' prior to this resolution.\n' + msj))

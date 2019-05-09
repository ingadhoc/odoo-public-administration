from odoo import fields, models, api


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
        required=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Councilor',
        domain=[('employee', '=', True)],
        required=True,
    )
    amount = fields.Integer(
        required=True,
    )
    subsidy_resolution_id = fields.Many2one(
        'public_budget.subsidy.resolution',
        ondelete='cascade',
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
        resolutions_with_expedient = self.search(
            [('expedient_id', '=', self.expedient_id.id)])
        if len(resolutions_with_expedient) > 0:
            return {
                'warning': {
                    'title': "El TA ya existe en estas resoluciones",
                    'message': " * " + "\n * ".join(
                        resolutions_with_expedient.mapped(lambda x: " - ".join(
                            [x.subsidy_resolution_id.date,
                             x.subsidy_resolution_id.name]))),
                }
            }

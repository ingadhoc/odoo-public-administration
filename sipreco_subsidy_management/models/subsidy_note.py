from odoo import fields, models


class PublicBudgetSubsidyNote(models.Model):

    _name = 'public_budget.subsidy.note'

    subsidy_id = fields.Many2one(
        'public_budget.subsidy',
        'Subsidy',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(
        required=True,
    )
    date = fields.Date(
        required=True,
        default=fields.Date.context_today
    )
    # type = fields.Selection([
    #     ('first', 'Primer reclamo'),
    #     ('last', 'Ultimo aviso')],
    #     'Tipo',
    #     required=True,
    # )
    type_id = fields.Many2one(
        'public_budget.subsidy.note.type',
        string='Tipo',
        required=True,
    )

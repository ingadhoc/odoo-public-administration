from odoo import models, fields


class ExpedientCategory(models.Model):

    _name = 'public_budget.expedient_category'
    _description = 'Expedient Category'

    name = fields.Char(
        required=True
    )

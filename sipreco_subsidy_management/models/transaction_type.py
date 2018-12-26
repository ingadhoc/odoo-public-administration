from odoo import fields, models


class PublicBudgetTransactionType(models.Model):

    _inherit = 'public_budget.transaction_type'

    subsidy = fields.Boolean(
    )

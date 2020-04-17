from odoo import models, fields


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    max_statement_operation = fields.Float(
    )

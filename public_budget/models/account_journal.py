from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    max_statement_operation = fields.Float(
        )

from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)


class PublicBudgetSubsidyNoteType(models.Model):

    _name = 'public_budget.subsidy.note.type'
    _order = 'sequence'

    sequence = fields.Integer(
        required=True,
        default=10,
    )
    name = fields.Char(
        required=True,
    )
    code = fields.Char(
        required=True,
    )

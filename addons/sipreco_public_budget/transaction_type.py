# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class transaction_type(models.Model):
    """Transaction Type"""

    _inherit = 'public_budget.transaction_type'

# TODO ver de implementar esto pero es un quilombo!
    # _partner_types_ = [
    #     # State machine: untitle
    #     ('supllier', 'Suplliers'),
    #     ('subsidy_recipient', 'Subsidy Recipients'),
    # ]

    # definitive_partner_type = fields.Selection(
    #     _partner_types_,
    #     'Definitive Partner Type',
    #     )
    # advance_partner_type = fields.Boolean(
    #     _partner_types_,
    #     'Advance Partner Type',
    #     )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
from openerp import models, fields


class transaction(models.Model):

    _inherit = 'public_budget.transaction'

    definitive_partner_type = fields.Selection(
        related='type_id.definitive_partner_type'
        )

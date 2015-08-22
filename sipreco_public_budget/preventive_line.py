# -*- coding: utf-8 -*-
from openerp import models, fields


class preventive_line(models.Model):

    _inherit = 'public_budget.preventive_line'

    definitive_partner_type = fields.Selection(
        related='transaction_id.type_id.definitive_partner_type'
        )

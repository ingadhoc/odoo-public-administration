# -*- coding: utf-8 -*-
from openerp import models, fields


class advance_request_type(models.Model):
    """"""

    _name = 'public_budget.advance_request_type'
    _description = 'Advance Request Type'

    name = fields.Char(
        'Name',
        required=True,
        )
    general_return_partner_id = fields.Many2one(
        'res.partner',
        string='General Return Partner',
        required=True
        )

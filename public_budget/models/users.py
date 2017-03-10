# -*- coding: utf-8 -*-
from openerp import models, fields


class ResUsers(models.Model):

    _inherit = ['res.users']

    location_ids = fields.Many2many(
        'public_budget.location',
        'public_budget_user_ids_location_ids_rel',
        'users_id',
        'location_id',
        string='Allowed Locations'
    )

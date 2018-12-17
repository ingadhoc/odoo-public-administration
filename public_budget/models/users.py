# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):

    _inherit = ['res.users']

    location_ids = fields.Many2many(
        'public_budget.location',
        'public_budget_user_ids_location_ids_rel',
        'users_id',
        'location_id',
        string='Allowed Locations'
    )

    category_ids = fields.Many2many(
        'public_budget.expedient_category',
        'public_budget_user_ids_category_ids_rel',
        'users_id',
        'category_id',
        string='Allowed Expedient Categories'
    )

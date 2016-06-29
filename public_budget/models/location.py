# -*- coding: utf-8 -*-
from openerp import models, fields


class location(models.Model):
    """Location"""

    _name = 'public_budget.location'
    _description = 'Location'

    _order = "name"

    name = fields.Char(
        string='Name',
        required=True
    )
    user_ids = fields.Many2many(
        'res.users',
        'public_budget_user_ids_location_ids_rel',
        'location_id',
        'users_id',
        string='Users'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

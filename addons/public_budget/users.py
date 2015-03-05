# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class users(models.Model):
    """"""

    _name = 'res.users'
    _inherits = {}
    _inherit = ['res.users']

    location_ids = fields.Many2many(
        'public_budget.location',
        'public_budget_user_ids_location_ids_rel',
        'users_id',
        'location_id',
        string='Locations'
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

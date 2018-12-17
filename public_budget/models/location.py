from odoo import models, fields


class Location(models.Model):

    _name = 'public_budget.location'
    _description = 'Location'

    _order = "name"

    name = fields.Char(
        required=True
    )
    user_ids = fields.Many2many(
        'res.users',
        'public_budget_user_ids_location_ids_rel',
        'location_id',
        'users_id',
        string='Users'
    )

from odoo import models, fields


class Location(models.Model):

    _name = 'public_budget.location'
    _inherit = ['mail.thread']
    _description = 'Location'

    _order = "name"

    name = fields.Char(
        required=True,
    )
    user_ids = fields.Many2many(
        'res.users',
        'public_budget_user_ids_location_ids_rel',
        'location_id',
        'users_id',
        string='Users'
    )
    user_id = fields.Many2one(
        'res.users',
        'Responsable',
        track_visibility='onchange',
    )

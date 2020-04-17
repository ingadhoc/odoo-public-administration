from odoo import models, fields, api


class Location(models.Model):

    _name = 'public_budget.location'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Location'
    _rec_name = 'complete_name'

    _order = "name"

    name = fields.Char(
        required=True,
    )
    complete_name = fields.Char(
        compute='_compute_complete_name',
        store=True,
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
        tracking=True,
    )
    asset_management = fields.Boolean('For asset management')
    expedient_management = fields.Boolean('For expedient management')
    level = fields.Char()
    number = fields.Char()
    building = fields.Char()
    active = fields.Boolean(
        tracking=True,
        default=True,
    )

    @api.depends('name', 'level', 'number', 'building')
    def _compute_complete_name(self):
        for location in self:
            name = location.name
            if location.level:
                name += '-' + location.level
            if location.number:
                name += '-' + location.number
            if location.building:
                name += '-' + location.building
            location.complete_name = name

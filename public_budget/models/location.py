from odoo import models, fields, api


class Location(models.Model):

    _name = 'public_budget.location'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
    asset_management = fields.Boolean('For asset management')
    expedient_management = fields.Boolean('For expedient management')
    level = fields.Char()
    number = fields.Char()
    building = fields.Char()

    @api.depends('name', 'level', 'number')
    def name_get(self):
        result = []
        for location in self:
            name = location.name
            if location.level:
                name += '-' + location.level
            if location.number:
                name += '-' + location.number
            result.append((location.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                '|', '|', '|', ('name', operator, name),
                ('level', operator, name),
                ('number', operator, name),
                ('building', operator, name), ]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

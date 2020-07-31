from odoo import models, fields, api


class ResUsers(models.Model):

    _inherit = 'res.users'

    location_ids = fields.Many2many(
        'public_budget.location',
        'public_budget_user_ids_location_ids_rel',
        'users_id',
        'location_id',
        string='Allowed Locations'
    )

    expedient_category_ids = fields.Many2many(
        'public_budget.expedient_category',
        'public_budget_user_ids_category_ids_rel',
        'users_id',
        'category_id',
        string='Allowed Expedient Categories'
    )
    public_portal_groups_ids = fields.Many2many(
        'res.groups',
        compute='_compute_public_portal_groups_ids',
        inverse='_inverse_public_portal_groups_ids',
        string='Portal Groups',
        domain=lambda self: [('category_id', '=', self.env.ref(
            'public_budget.category_public_budget_portal', raise_if_not_found=False) and self.env.ref(
            'public_budget.category_public_budget_portal', raise_if_not_found=False).id or False)],
    )
    is_portal_user = fields.Boolean(
        compute='_compute_is_portal_user',
    )

    @api.depends('groups_id')
    def _compute_is_portal_user(self):
        for rec in self:
            rec.is_portal_user = rec.groups_id.filtered(
                lambda g: g == self.env.ref('base.group_portal')) or False

    def _inverse_public_portal_groups_ids(self):
        for rec in self:
            rec.groups_id = rec.public_portal_groups_ids

    def _compute_public_portal_groups_ids(self):
        portal_group = self.env.ref('public_budget.category_public_budget_portal', raise_if_not_found=False) or None
        if not portal_group:
            self.update({'public_portal_groups_ids': self.env['res.groups']})
        for rec in self:
            groups = rec.groups_id.filtered(
                lambda g: g.category_id == portal_group)
            rec.public_portal_groups_ids = groups

    @api.model
    def systray_get_activities(self):
        """ We did this to avoid errors when use portal user when the module "Note" is not a depends of this module.
        Only apply this change if the user is portal.
        """
        if self.env.user.has_group('base.group_portal') and self.env['ir.module.module'].sudo().search(
                [('name', '=', 'note')]).state == 'installed':
            self = self.sudo()
        return super().systray_get_activities()

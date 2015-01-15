# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import Warning


class public_budget_expedients_move_wizard(models.TransientModel):
    _name = 'public_budget.expedients_move_wizard'
    _description = 'Expedients Move Wizard'

    date = fields.Datetime(
        'Date',
        default=fields.Datetime.now,
        readonly=True,
        required=True,
        )

    user_id = fields.Many2one(
        'res.users',
        'User',
        default=lambda self: self.env.user,
        readonly=True,
        required=True,
        )

    location_id = fields.Many2one(
        'public_budget.location',
        'Source Location',
        required=True,
        )

    location_dest_id = fields.Many2one(
        'public_budget.location',
        'Destiny Location',
        required=True,
        )

    expedient_ids = fields.Many2many(
        'public_budget.expedient',
        'expedient_moves_expedient_rel',
        string='Expedients',
        required=True,
        )

    @api.one
    @api.constrains('location_id', 'location_dest_id')
    def check_locations(self):
        if self.location_id == self.location_dest_id:
            raise Warning(
                _('Source Location and Destiny Location can not be the same'))

    @api.onchange('location_id')
    def onchange_location_id(self):
        self.expedient_ids = []

    @api.multi
    def confirm_move(self):
        move_ids = []
        for expedient in self.expedient_ids:
            vals = {
                'expedient_id': expedient.id,
                'date': self.date,
                'user_id': self.user_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
            }
            move_ids.append(expedient.expedient_move_ids.create(vals).id)
        tree_view = self.env['ir.model.data'].get_object_reference(
            'public_budget', 'view_public_budget_expedient_move2_tree')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Expedient Moves'),
            'res_model': 'public_budget.expedient_move',
            'domain': "[('id','in',["+','.join(map(str, move_ids))+"])]",
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': tree_view[1],
            'target': 'current',
            'nodestroy': True,
        }
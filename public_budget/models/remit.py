# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class Remit(models.Model):

    _name = 'public_budget.remit'
    _description = 'Remit'
    _rec_name = 'number'

    _order = "date desc"

    _states_ = [
        ('in_transit', 'In Transit'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancel'),
    ]

    number = fields.Char(
        readonly=True
    )
    date = fields.Datetime(
        readonly=True,
        required=True,
        default=lambda self: fields.Datetime.now()
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        readonly=True,
        required=True,
        default=lambda self: self.env.user
    )
    confirmation_user_id = fields.Many2one(
        'res.users',
        string='Confirmation User',
        readonly=True,
    )
    confirmation_date = fields.Datetime(
        string='Confirmation Date',
        readonly=True,
    )
    location_id = fields.Many2one(
        'public_budget.location',
        string='Source Location',
        readonly=True,
        required=True,
        states={'in_transit': [('readonly', False)]}
    )
    location_dest_id = fields.Many2one(
        'public_budget.location',
        string='Destination Location',
        readonly=True,
        required=True,
        states={'in_transit': [('readonly', False)]}
    )
    reference = fields.Char(
        string='Referencia',
        readonly=False
    )
    user_location_ids = fields.Many2many(
        compute='get_user_locations',
        comodel_name='public_budget.location',
        string='User Locations',
    )
    state = fields.Selection(
        _states_,
        default='in_transit',
    )
    expedient_ids = fields.Many2many(
        'public_budget.expedient',
        'public_budget_remit_ids_expedient_ids_rel',
        'remit_id',
        'expedient_id',
        string='Expedients'
    )

    @api.multi
    # dummy depends to compute values on create
    @api.depends('state')
    def get_user_locations(self):
        for rec in self:
            rec.user_location_ids = rec.env.user.location_ids

    @api.multi
    @api.constrains('state')
    def check_state(self):
        for rec in self:
            if rec.state == 'cancel':
                for expedient in rec.expedient_ids:
                    remits = rec.search([
                        ('expedient_ids', '=', expedient.id)],
                        order='date desc')
                    if remits[0] != rec:
                        raise ValidationError(_(
                            'You can Not cancel a remit that is not the last '
                            'one for all the expedients'))

    @api.multi
    @api.constrains('date', 'expedient_ids')
    def check_dates(self):
        for rec in self:
            future_expedients = rec.expedient_ids.search([
                ('last_move_date', '>', rec.date),
                ('id', 'in', rec.expedient_ids.ids),
            ])
            if future_expedients:
                raise ValidationError(
                    'No puede mover expedientes que hayan sido movidos en un '
                    'remito con fecha mayor a la de este remito!\n'
                    '* Expedientes: %s' % (', '.join(
                        future_expedients.mapped('number'))))

    @api.multi
    def check_user_location(self):
        for rec in self:
            rec.confirmation_user_id = rec.env.user
            rec.confirmation_date = fields.Datetime.now()
            if rec.location_dest_id not in rec.env.user.location_ids:
                raise ValidationError(_(
                    'You can Not Confirme a Remit of a Location where your '
                    'are not authorized!'))

    @api.multi
    def action_cancel_in_transit(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'in_transit'})
        return True

    @api.multi
    def action_cancel(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_confirm(self):
        """ go from canceled state to draft state"""
        self.check_user_location()
        self.write({'state': 'confirmed'})
        return True

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'cancel':
                raise ValidationError(_(
                    "You can not delete a Remit that is not in Cancel State"))
            return super(Remit, rec).unlink()

    @api.model
    def create(self, vals):
        # con sudo para usuarios portal
        vals['number'] = self.sudo().env[
            'ir.sequence'].next_by_code('public_budget.remit') or '/'
        return super(Remit, self).create(vals)

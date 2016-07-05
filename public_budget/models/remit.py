# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class remit(models.Model):
    """Remit"""

    _name = 'public_budget.remit'
    _description = 'Remit'
    _rec_name = 'number'

    _order = "date desc"

    _states_ = [
        # State machine: untitle
        ('in_transit', 'In Transit'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancel'),
    ]

    number = fields.Char(
        string='Number',
        readonly=True
    )
    date = fields.Datetime(
        string='Date',
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
        comodel_name='public_budget.location',
        string='User Locations',
        related='user_id.location_ids'
    )
    state = fields.Selection(
        _states_,
        'State',
        default='in_transit',
    )
    expedient_ids = fields.Many2many(
        'public_budget.expedient',
        'public_budget_remit_ids_expedient_ids_rel',
        'remit_id',
        'expedient_id',
        string='Expedients'
    )

    @api.one
    @api.constrains('state')
    def check_state(self):
        if self.state == 'cancel':
            for expedient in self.expedient_ids:
                remits = self.search([
                    ('expedient_ids', '=', expedient.id)],
                    order='date desc')
                if remits[0] != self:
                    raise Warning(_(
                        'You can Not cancel a remit that is not the last one '
                        'for all the expedients'))

    @api.one
    @api.constrains('date', 'expedient_ids')
    def check_dates(self):
        future_expedients = self.expedient_ids.search([
            ('last_move_date', '>', self.date),
            ('id', 'in', self.expedient_ids.ids),
        ])
        if future_expedients:
            raise Warning(
                'No puede mover expedientes que hayan sido movidos en un '
                'remito con fecha mayor a la de este remito!\n'
                '* Expedientes: %s' % (', '.join(
                    future_expedients.mapped('number'))))

    @api.one
    def check_user_location(self):
        self.confirmation_user_id = self.env.user
        self.confirmation_date = fields.Datetime.now()
        if self.location_dest_id not in self.env.user.location_ids:
            raise Warning(_(
                'You can Not Confirme a Remit of a Location where your are not'
                ' authorized!'))

    @api.multi
    def action_cancel_in_transit(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'in_transit'})
        self.delete_workflow()
        self.create_workflow()
        return True

    @api.one
    def unlink(self):
        if self.state != 'cancel':
            raise Warning(_(
                "You can not delete a Remit that is not in Cancel State"))
        return super(remit, self).unlink()

    @api.model
    def create(self, vals):
        vals['number'] = self.env[
            'ir.sequence'].get('public_budget.remit') or '/'
        return super(remit, self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

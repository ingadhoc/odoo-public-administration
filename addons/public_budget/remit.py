# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class remit(models.Model):
    """Remit"""

    _name = 'public_budget.remit'
    _description = 'Remit'

    _order = "date desc"

    _states_ = [
        # State machine: untitle
        ('in_transit', 'In Transit'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancel'),
    ]

    date = fields.Datetime(
        string='Date',
        required=True,
        default=lambda self: fields.datetime.now()
        )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        readonly=True,
        required=True,
        default=lambda self: self.env.user
        )
    location_id = fields.Many2one(
        'public_budget.location',
        string='Source Location',
        required=True
        )
    location_dest_id = fields.Many2one(
        'public_budget.location',
        string='Destination Location',
        required=True
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
        string='Expedients',
        required=True
        )

    _constraints = [
    ]

    @api.multi
    def action_cancel_in_transit(self):
        # go from canceled state to draft state
        self.write({'state': 'in_transit'})
        self.delete_workflow()
        self.create_workflow()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

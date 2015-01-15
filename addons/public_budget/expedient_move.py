# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class expedient_move(models.Model):
    """Expedient Move"""

    _name = 'public_budget.expedient_move'
    _description = 'Expedient Move'

    _order = "date desc"

    date = fields.Datetime(
        string='Date',
        required=True,
        default=lambda self: fields.datetime.now()
        )
    user_id = fields.Many2one(
        'res.users',
        string='User',
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
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        ondelete='cascade',
        string='Expedient',
        required=True
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

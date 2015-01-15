# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class expedient_move(models.Model):
    """Expedient Move"""

    _name = 'public_budget.expedient_move'
    _description = 'Expedient Move'

    _order = "date desc"

    @api.model
    def _get_current_location(self):
        expedient_id = self._context.get('expedient', False)
        location_id = False
        if isinstance(expedient_id, int):
            expedient = self.env['public_budget.expedient'].search([
                ('id', '=', expedient_id)])
            if expedient.current_location_id:
                location_id = expedient.current_location_id.id
        return location_id

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
        default=_get_current_location,
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

# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class location(models.Model):
    """Location"""

    _name = 'public_budget.location'
    _description = 'Location'

    _order = "name"

    name = fields.Char(
        string='Name',
        required=True
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

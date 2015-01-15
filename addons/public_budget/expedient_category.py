# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class expedient_category(models.Model):
    """Expedient Category"""

    _name = 'public_budget.expedient_category'
    _description = 'Expedient Category'

    name = fields.Char(
        string='Name',
        required=True
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

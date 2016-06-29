# -*- coding: utf-8 -*-
from openerp import models, fields


class expedient_category(models.Model):
    """Expedient Category"""

    _name = 'public_budget.expedient_category'
    _description = 'Expedient Category'

    name = fields.Char(
        string='Name',
        required=True
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

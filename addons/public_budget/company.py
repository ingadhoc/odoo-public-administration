# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class company(models.Model):
    """"""

    _name = 'res.company'
    _inherits = {}
    _inherit = ['res.company']

    inventory_rule_ids = fields.One2many(
        'public_budget.inventory_rule',
        'company_id',
        string='Inventory Rules'
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

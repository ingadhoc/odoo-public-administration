# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class inventory_rule(models.Model):
    """"""

    _name = 'public_budget.inventory_rule'
    _description = 'inventory_rule'

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today
        )
    min_amount = fields.Float(
        string='Minimum Amount',
        required=True
        )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env['res.company']._company_default_get('public_budget.inventory_rule')
        )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

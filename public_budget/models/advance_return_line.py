# -*- coding: utf-8 -*-
from openerp import models, fields
import openerp.addons.decimal_precision as dp


class advance_return_line(models.Model):
    """"""

    _name = 'public_budget.advance_return_line'
    _description = 'advance_return_line'

    employee_id = fields.Many2one(
        'res.partner',
        string='Employee',
        required=True,
        context={'default_employee': 1},
        domain=[('employee', '=', True)]
        )
    debt_amount = fields.Float(
        string='Debt Amount',
        required=True,
        digits=dp.get_precision('Account'),
        )
    returned_amount = fields.Float(
        string='Returned Amount',
        required=True,
        digits=dp.get_precision('Account'),
        )
    advance_return_id = fields.Many2one(
        'public_budget.advance_return',
        ondelete='cascade',
        string='advance_return_id',
        required=True
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

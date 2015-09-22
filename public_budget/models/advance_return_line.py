# -*- coding: utf-8 -*-
from openerp import models, fields, api
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
        compute='_get_amounts',
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
        required=True,
        auto_join=True
        )
    state = fields.Selection(
        related='advance_return_id.state',
        )

    @api.one
    @api.depends(
        'employee_id',
        )
    def _get_amounts(self):
        if self.employee_id:
            self.debt_amount = self.employee_id.get_debt_amount(
                self.advance_return_id.type_id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

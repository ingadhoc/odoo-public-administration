# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AdvanceReturnLine(models.Model):

    _name = 'public_budget.advance_return_line'
    _description = 'Advance Return Lines'

    employee_id = fields.Many2one(
        'res.partner',
        string='Employee',
        required=True,
        context={'default_employee': 1},
        domain=[('employee', '=', True)]
    )
    debt_amount = fields.Monetary(
        string='Debt Amount',
        required=True,
        compute='_get_amounts',
    )
    returned_amount = fields.Monetary(
        string='Returned Amount',
        required=True,
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
    currency_id = fields.Many2one(
        related='advance_return_id.company_id.currency_id',
        readonly=True,
    )

    @api.multi
    @api.depends(
        'employee_id',
    )
    def _get_amounts(self):
        for rec in self:
            if rec.employee_id:
                rec.debt_amount = rec.employee_id.get_debt_amount(
                    rec.advance_return_id.type_id)

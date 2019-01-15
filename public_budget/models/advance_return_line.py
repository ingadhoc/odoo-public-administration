from odoo import models, fields, api


class AdvanceReturnLine(models.Model):

    _name = 'public_budget.advance_return_line'
    _description = 'Advance Return Lines'

    employee_id = fields.Many2one(
        'res.partner',
        required=True,
        context={'default_employee': 1},
        domain=[('employee', '=', True)]
    )
    debt_amount = fields.Monetary(
        required=True,
        compute='_compute_amounts',
    )
    returned_amount = fields.Monetary(
        required=True,
    )
    advance_return_id = fields.Many2one(
        'public_budget.advance_return',
        ondelete='cascade',
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

    @api.depends(
        'employee_id',
    )
    def _compute_amounts(self):
        for rec in self.filtered('employee_id'):
            rec.debt_amount = rec.employee_id.get_debt_amount(
                rec.advance_return_id.type_id)

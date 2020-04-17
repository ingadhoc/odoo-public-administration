from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AdvanceRequestLine(models.Model):

    _name = 'public_budget.advance_request_line'
    _description = 'Advance Request Line'

    employee_id = fields.Many2one(
        'res.partner',
        required=True,
        context={'default_employee': 1},
        domain=[('employee', '=', True)]
    )
    requested_amount = fields.Monetary(
        required=True,
    )
    description = fields.Char(
    )
    debt_amount = fields.Monetary(
        compute='_compute_amounts',
    )
    pending_return_amount = fields.Monetary(
        help='Monto de Devolucion Pendiente de Confirmación en devolución '
        'de adelanto',
        compute='_compute_amounts',
    )
    approved_amount = fields.Monetary(
    )
    advance_request_id = fields.Many2one(
        'public_budget.advance_request',
        ondelete='cascade',
        required=True,
        auto_join=True
    )
    state = fields.Selection(
        related='advance_request_id.state',
        readonly=False,
    )
    currency_id = fields.Many2one(
        related='advance_request_id.company_id.currency_id',
    )

    @api.depends(
        'employee_id',
    )
    def _compute_amounts(self):
        for rec in self.filtered('employee_id'):
            request_type = rec.advance_request_id.type_id
            rec.debt_amount = rec.employee_id.get_debt_amount(
                request_type)
            pending_return_domain = [
                ('employee_id', '=', rec.employee_id.id),
                ('advance_return_id.state', 'in', ['draft']),
                ('advance_return_id.type_id', '=', request_type.id),
            ]
            rec.pending_return_amount = sum(
                self.env['public_budget.advance_return_line'].search(
                    pending_return_domain).mapped('returned_amount'))

    @api.onchange('requested_amount')
    def change_(self):
        self.approved_amount = self.requested_amount

    @api.constrains('requested_amount', 'approved_amount')
    def check_amounts(self):
        if self.filtered(
                lambda x: x.approved_amount > x.requested_amount):
            raise ValidationError(_(
                'Approved Amount can not be greater than Requested Amount'))

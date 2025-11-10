from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AdvanceRequestType(models.Model):

    _name = 'public_budget.advance_request_type'
    _description = 'Advance Request Type'
    _check_company_auto = True

    name = fields.Char(
        required=True,
    )
    general_return_partner_id = fields.Many2one(
        'res.partner',
        required=True
    )
    account_id = fields.Many2one(
        'account.account',
        domain=[('deprecated', '=', False), ('account_type', 'not in', ['asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card'])],
        # ahora no queremos que sea payable porque no queremos que se lleve
        # a la deuda del partner generico, queremos que para que se lleve haga
        # falta hacer una devolucion
        required=True,
        check_company=True,
    )
    return_journal_id = fields.Many2one(
        'account.journal',
        required=True,
        check_company=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    employee_ids = fields.Many2many(
        'res.partner',
        compute='_compute_employee_ids',
    )

    def _compute_employee_ids(self):
        self.employee_ids = False
        for rec in self:
            employees = self.env['res.partner'].search(
                [('employee', '=', True)]).filtered(
                lambda x: x.get_debt_amount(rec))
            for employee in employees:
                rec.employee_ids = [(4, employee.id, False)]

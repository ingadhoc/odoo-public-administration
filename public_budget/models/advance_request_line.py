# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning


class advance_request_line(models.Model):
    """Advance Request Line"""

    _name = 'public_budget.advance_request_line'
    _description = 'Advance Request Line'

    employee_id = fields.Many2one(
        'res.partner',
        string='Employee',
        required=True,
        context={'default_employee': 1},
        domain=[('employee', '=', True)]
        )
    requested_amount = fields.Float(
        string='Requested Amount',
        required=True,
        digits=dp.get_precision('Account'),
        )
    description = fields.Char(
        string='Description',
        )
    debt_amount = fields.Float(
        string=_('Debt Amount'),
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        )
    pending_return_amount = fields.Float(
        string='Devolucion Pendiente',
        help='Monto de Devolucion Pendiente de Confirmación en devolución '
        'de adelanto',
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        )
    approved_amount = fields.Float(
        string='Approved Amount',
        digits=dp.get_precision('Account'),
        )
    advance_request_id = fields.Many2one(
        'public_budget.advance_request',
        ondelete='cascade',
        string='advance_request_id',
        required=True,
        auto_join=True
        )
    state = fields.Selection(
        related='advance_request_id.state',
        )
    # voucher_id = fields.Many2one(
    #     'account.voucher',
    #     'Voucher',
    #     readonly=True,
    #     )

    @api.one
    @api.depends(
        'employee_id',
        )
    def _get_amounts(self):
        if self.employee_id:
            request_type = self.advance_request_id.type_id
            self.debt_amount = self.employee_id.get_debt_amount(
                request_type)
            pending_return_domain = [
                ('employee_id', '=', self.employee_id.id),
                ('advance_return_id.state', 'in', ['draft']),
                ('advance_return_id.type_id', '=', request_type.id),
                ]
            self.pending_return_amount = sum(
                self.env['public_budget.advance_return_line'].search(
                    pending_return_domain).mapped('returned_amount'))

    @api.onchange('requested_amount')
    def change_(self):
        self.approved_amount = self.requested_amount

    @api.one
    @api.constrains('requested_amount', 'approved_amount')
    def check_amounts(self):
        if self.approved_amount > self.requested_amount:
            raise Warning(_(
                'Approved Amount can not be greater than Requested Amount'))

    # old method that make on voucher per each line/employee. Now we make
    # one voucher for all employess, we keep it just in case they want
    # this usability again
    # @api.multi
    # def create_voucher(self):
    #     vouchers = self.env['account.voucher']
    #     for line in self:
    #         request = line.advance_request_id
    #         amount = line.approved_amount
    #         journal = self.env['account.journal'].search([
    #             ('company_id', '=', request.company_id.id),
    #             ('type', 'in', ('cash', 'bank'))], limit=1)
    #         if not journal:
    #             raise Warning(_(
    #                 'No bank or cash journal found for company "%s"') % (
    #                 request.company_id.name))
    #         partner = line.employee_id
    #         currency = journal.currency or request.company_id.currency_id
    #         voucher_data = vouchers.onchange_partner_id(
    #             partner.id, journal.id, 0.0,
    #             currency.id, 'payment', False)
    #         voucher_vals = {
    #             'type': 'payment',
    #             'partner_id': partner.id,
    #             'journal_id': journal.id,
    #             'advance_amount': amount,
    #             'account_id': voucher_data['value'].get('account_id', False),
    #             }
    #         voucher = vouchers.create(voucher_vals)
    #         line.voucher_id = voucher.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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
    voucher_id = fields.Many2one(
        'account.voucher',
        'Voucher',
        readonly=True,
        )

    @api.one
    @api.depends(
        'employee_id',
        )
    def _get_amounts(self):
        if self.employee_id:
            self.debt_amount = self.employee_id.get_debt_amount(
                self.advance_request_id.type_id)

    @api.one
    @api.constrains('requested_amount', 'approved_amount')
    def check_amounts(self):
        if self.approved_amount > self.requested_amount:
            raise Warning(_(
                'Approved Amount can not be greater than Requested Amount'))

    @api.multi
    def create_voucher(self):
        vouchers = self.env['account.voucher']
        for line in self:
            request = line.advance_request_id
            amount = line.approved_amount
            journal = self.env['account.journal'].search([
                ('company_id', '=', request.company_id.id),
                ('type', 'in', ('cash', 'bank'))], limit=1)
            if not journal:
                raise Warning(_(
                    'No bank or cash journal found for company "%s"') % (
                    request.company_id.name))
            partner = line.employee_id
            currency = journal.currency or request.company_id.currency_id
            voucher_data = vouchers.onchange_partner_id(
                partner.id, journal.id, 0.0,
                currency.id, 'payment', False)
            print 'voucher_data', voucher_data
            print 'journal', journal
            print 'currency', currency
            # we dont want to pay anything
            # line_cr_ids = [
            #     (0, 0, vals) for vals in voucher_data['value'].get(
            #         'line_cr_ids', False) if isinstance(vals, dict)]
            # line_dr_ids = [
            #     (0, 0, vals) for vals in voucher_data['value'].get(
            #         'line_dr_ids', False) if isinstance(vals, dict)]
            voucher_vals = {
                'type': 'payment',
                # 'receiptbook_id': self.budget_id.receiptbook_id.id,
                # 'expedient_id': self.expedient_id.id,
                'partner_id': partner.id,
                # 'transaction_id': self.id,
                'journal_id': journal.id,
                'advance_amount': amount,
                'account_id': voucher_data['value'].get('account_id', False),
                # 'line_cr_ids': line_cr_ids,
                # 'line_dr_ids': line_dr_ids,
                }
            voucher = vouchers.create(voucher_vals)
            line.voucher_id = voucher.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

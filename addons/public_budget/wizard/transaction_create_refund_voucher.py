# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
import time
from openerp.exceptions import Warning


class public_budget_transaction_create_refund_voucher(models.TransientModel):
    _name = 'public_budget.transaction_create_refund_voucher'
    _description = 'Transaction Create Refund Voucher'

    @api.model
    def _get_transaction_id(self):
        return self._context.get('active_id', False)

    @api.one
    @api.depends('transaction_id')
    def get_partner(self):
        self.partner_id = self.transaction_id.partner_id

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        compute='get_partner',
        # domain=[('is_employee', '=', True)],
        required=True)

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('type', 'in', ('cash', 'bank'))],
        required=True)

    transaction_id = fields.Many2one(
        'public_budget.transaction',
        'Transaction',
        default=_get_transaction_id,
        required=True
    )

    amount = fields.Float('Amount', required=True)

    @api.one
    def create_voucher(self):
        # journal = False
        # journal_id = self.env['account.voucher']._get_journal()
        # journal = self.env['account.journal'].browse(journal_id)
        journal = self.journal_id
        if not journal:
            raise Warning(_("Not Journal Found"))
        # TODO get journal
        if self.amount > self.transaction_id.advance_remaining_amount:
            raise Warning(_("Amount Can't be greater than Advance Remaining Amount"))

        currency = journal.currency or journal.company_id.currency_id
        result = self.env['account.voucher'].onchange_partner_id(
            partner_id=self.partner_id.id,
            journal_id=journal.id,
            amount=self.amount,
            currency_id=currency.id,
            ttype='receipt',
            date=time.strftime('%Y-%m-%d'),
            )

        account_id = result['value'].get(
            'account_id', journal.default_credit_account_id.id)
        voucher_res = {
            'type': 'receipt',
            # 'name': line.name,
            'partner_id': self.partner_id.id,
            'journal_id': journal.id,
            'account_id': account_id,
            'company_id': journal.company_id.id,
            'currency_id': currency.id,
            'date': time.strftime('%Y-%m-%d'),
            'amount': self.amount,
            'payment_option': 'with_writeoff',
            'writeoff_acc_id': self.transaction_id.type_id.advance_account_id.id,
            'comment': self.transaction_id.type_id.advance_account_id.name,
            'transaction_id': self.transaction_id.id
            # 'period_id': statement.period_id.id,
        }
        voucher = self.env['account.voucher'].create(voucher_res)
        voucher.signal_workflow(
            'proforma_voucher')
            # 'proforma_confirmed')
        return voucher

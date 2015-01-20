# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import time
from openerp.exceptions import Warning


class payment_line(models.Model):
    _inherit = "payment.line"
    voucher_id = fields.Many2one('account.voucher', 'Voucher', readonly=True)


class payment_order(models.Model):
    _inherit = "payment.order"

    voucher_ids = fields.One2many(
        'account.voucher', 'payment_order_id', 'Vouchers', readonly=True)

    @api.one
    def _voucher_count(self):
        self.voucher_count = len(self.voucher_ids)

    voucher_count = fields.Integer('Vouchers', compute="_voucher_count")

    @api.multi
    def set_done(self):
        self.create_voucher()
        return super(payment_order, self).set_done()

    @api.one
    def unlink(self):
        if self.voucher_ids:
            raise Warning(_("You can delete a Payment Order with Vouchers."))
        return super(payment_order, self).unlink()

    @api.one
    def action_cancel_payments(self):
        for voucher in self.voucher_ids:
            if voucher.state not in ('draft', 'cancel'):
                raise Warning(_("You can cancel a Payment Order with Vouchers in states different from 'draft' or 'cancel'."))
            self.voucher_ids.write({'payment_order_id': False})
            self.voucher_ids.unlink()
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

    @api.one
    def create_voucher(self):
        move_line_obj = self.pool.get('account.move.line')

        voucher_ids = []
        journal = self.mode.journal
        currency = journal.currency or journal.company_id.currency_id
        for line in self.line_ids:
            if line.voucher_id:
                continue
            result = self.env['account.voucher'].onchange_partner_id(
                partner_id=line.partner_id.id,
                journal_id=journal.id,
                amount=abs(line.amount),
                currency_id=currency.id,
                ttype='payment',
                date=line.ml_maturity_date)

            account_id = result['value'].get(
                'account_id', journal.default_credit_account_id.id)
            voucher_res = {
                'type': 'payment',
                'name': line.name,
                'partner_id': line.partner_id.id,
                'journal_id': journal.id,
                'account_id': account_id,
                'company_id': self.company_id.id,
                'currency_id': currency.id,
                'date': line.date or time.strftime('%Y-%m-%d'),
                'amount': abs(line.amount),
                'payment_order_id': self.id
            }
            voucher = self.env['account.voucher'].create(voucher_res)
            if self.transaction_id.type_id.with_advance_payment:
                if not self.transaction_id.type_id.advance_account_id:
                    raise Warning(_('In advance transactions you should configure an advance account on the Transaction Type'))
                voucher_vals = {
                    'payment_option': 'with_writeoff',
                    'writeoff_acc_id': self.transaction_id.type_id.advance_account_id.id,
                    'comment': self.transaction_id.type_id.advance_account_id.name,
                    }
                voucher.write(voucher_vals)
            else:
                voucher_line_dict = {}
                for line_dict in result[
                        'value']['line_cr_ids'] + result[
                        'value']['line_dr_ids']:
                    move_line = move_line_obj.browse(
                        self._cr, self._uid, line_dict['move_line_id'],
                        self._context)
                    if line.move_line_id.move_id.id == move_line.move_id.id:
                        voucher_line_dict = line_dict

                if voucher_line_dict:
                    voucher_line_dict.update({'voucher_id': voucher.id})
                    self.env['account.voucher.line'].create(
                        voucher_line_dict)
            line.voucher_id = voucher.id
            voucher_ids.append(voucher.id)
        return voucher_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

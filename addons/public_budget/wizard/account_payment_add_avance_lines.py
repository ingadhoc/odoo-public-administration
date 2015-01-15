# -*- coding: utf-8 -*-
from openerp import fields, models, api


class payment_add_avance_lines(models.TransientModel):
    _name = 'payment.add.advance_lines'
    _description = 'Payment Order Add Advance Lines'

    @api.model
    def _get_transaction_id(self):
        return self._context.get('transaction_id', False)

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

    transaction_id = fields.Many2one(
        'public_budget.transaction',
        'Transaction',
        default=_get_transaction_id,
        required=True
    )

    advance_preventive_line_ids = fields.Many2many(
        'public_budget.preventive_line',
        string='Advance Preventive Lines',
        required=True,
    )

    @api.one
    @api.onchange('transaction_id')
    def _get_advance_preventive_lines(self):
        self.advance_preventive_line_ids = advance_line_ids = self.env[
            'public_budget.preventive_line']
        advance_line_ids = advance_line_ids.search([
            ('transaction_id', '=', self.transaction_id.id),
            ('payment_line_id', '=', False),
            ('advance_line', '=', True),
        ])
        self.advance_preventive_line_ids = advance_line_ids.ids

    @api.one
    def create_payment_lines(self):
        # order_obj = self.pool.get('payment.order')
        # line_obj = self.pool.get('account.move.line')
        payment_line = self.env['payment.line']
        payment_id = self._context.get('active_id', False)
        if not payment_id:
            return False
        payment = self.env['payment.order'].browse(payment_id)
        for line in self.advance_preventive_line_ids:
            vals = {
                'partner_id': self.partner_id.id,
                'bank_id': self.partner_id.bank_ids and self.partner_id.bank_ids[0].id,
                'amount_currency': line.preventive_amount,
                'communication': line.name or '/',
                'order_id': payment_id,
                'currency': payment.mode.journal.currency.id or payment.mode.journal.company_id.currency_id.id,
                # TODO la fecha de pago cual deberia ser?
                # 'date': date_to_pay,
            }
            payment_line = payment_line.create(vals)
            line.payment_line_id = payment_line.id
        # line_ids = [entry.id for entry in data.entries]
        # if not line_ids:
        #     return {'type': 'ir.actions.act_window_close'}

        # payment = order_obj.browse(cr, uid, context['active_id'], context=context)
        # t = None
        # line2bank = line_obj.line2bank(cr, uid, line_ids, t, context)

        # Finally populate the current payment with new lines:
        # for line in line_obj.browse(cr, uid, line_ids, context=context):
        #     if payment.date_prefered == "now":
        # no payment date => immediate payment
        #         date_to_pay = False
        #     elif payment.date_prefered == 'due':
        #         date_to_pay = line.date_maturity
        #     elif payment.date_prefered == 'fixed':
        #         date_to_pay = payment.date_scheduled
        #     payment_obj.create(cr, uid,{
        #             'move_line_id': line.id,
        #             'amount_currency': line.amount_residual_currency,
        #             'bank_id': line2bank.get(line.id),
        #             'order_id': payment.id,
        #             'partner_id': line.partner_id and line.partner_id.id or False,
        #             'communication': line.ref or '/',
        #             'state': line.invoice and line.invoice.reference_type != 'none' and 'structured' or 'normal',
        #             'date': date_to_pay,
        #             'currency': (line.invoice and line.invoice.currency_id.id) or line.journal_id.currency.id or line.journal_id.company_id.currency_id.id,
        #         }, context=context)
        # return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class account_move_line(models.Model):
    _inherit = ['account.move.line']

    voucher_line_ids = fields.One2many(
        'account.voucher.line',
        'move_line_id',
        'Voucher Lines'
        )


class invoice(models.Model):
    """"""
    # TODO validar que la factura
    # no se pueda validar en un fiscalyear distinto al del budget id
    _name = 'account.invoice'
    _inherits = {}
    _inherit = ['account.invoice']

    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transaction',
        copy=False,
        readonly=True,
        # required=True,
        )
    budget_id = fields.Many2one(
        related='transaction_id.budget_id',
        readonly=True,
        store=True,
        )
    signed_amount = fields.Float(
        _('Signed Amount'),
        compute='get_signed_amount',
        )
    to_pay_amount = fields.Float(
        string=_('To Pay Amount'),
        digits=dp.get_precision('Account'),
        compute='_compute_to_pay_amount',
        # store=True, #TODO ver si lo hacemos stored
        )

    @api.one
    @api.depends('type', 'amount_total')
    def get_signed_amount(self):
        if self.type in ('in_refund', 'out_refund'):
            signed_amount = -1.0 * self.amount_total
        else:
            signed_amount = self.amount_total
        self.signed_amount = signed_amount

    @api.one
    @api.depends(
        'state', 'currency_id',
        'move_id.line_id.voucher_line_ids.amount',
        'move_id.line_id.voucher_line_ids.voucher_id.state',
    )
    # An invoice's to pay amount is the sum of its unreconciled move lines and,
    # for partially reconciled move lines, their residual amount divided by the
    # number of times this reconciliation is used in an invoice (so we split
    # the residual amount between all invoice)
    def _compute_to_pay_amount(self):
        paid_amount = self.amount_total - self.residual
        voucher_lines = self.env['account.voucher.line'].search([
            ('move_line_id.move_id', '=', self.move_id.id),
            ('amount', '!=', 0),
            ('voucher_id.state', 'not in', ('cancel', 'draft')),
            ])
        to_pay_amount = sum([x.amount for x in voucher_lines])
        if paid_amount > to_pay_amount:
            to_pay_amount = paid_amount
        self.to_pay_amount = to_pay_amount

    @api.multi
    def action_cancel(self):
        for inv in self:
            if inv.to_pay_amount:
                raise Warning(_(
                    'You cannot cancel an invoice which has been sent to pay.\
                    You need to cancel related payments first.'))
        return super(invoice, self).action_cancel()

    @api.multi
    def invoice_validate(self):
        res = super(invoice, self).invoice_validate()
        for inv in self:
            if inv.transaction_id.type_id.with_advance_payment:
                domain = [
                    ('move_id', '=', inv.move_id.id),
                    ('account_id', '=', inv.account_id.id),
                ]
                move_lines = self.env['account.move.line'].search(domain)
                move_lines.write(
                    {'partner_id': self.transaction_id.partner_id.id})
        return res

    @api.multi
    def prepare_direct_payment_voucher_vals(self):
        """Add some values to direct payment voucher creation"""
        if not self.transaction_id:
            raise Warning(_('Not Transaction in actual invoice, can not create\
             direct Payment'))
        res = super(
            invoice, self).prepare_direct_payment_voucher_vals()
        res['transaction_id'] = self.transaction_id.id
        res['expedient_id'] = self.transaction_id.expedient_id.id
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transaction',
        copy=False,
        readonly=True,
        auto_join=True,
        # required=True,
    )
    budget_id = fields.Many2one(
        related='transaction_id.budget_id',
        readonly=True,
        store=True,
        auto_join=True,
    )
    to_pay_amount = fields.Monetary(
        string='Monto A Pagar',
        # compute='_compute_to_pay_amount',
        # store=True,
    )

    @api.multi
    @api.constrains('state')
    def update_definitive_invoiced_amount(self):
        # this method update all amounts on the upstream
        _logger.info('Updating invoice line amounts from invoice')
        for rec in self:
            # if invoice state changes, we recompute to_pay_amount
            rec.sudo()._compute_to_pay_amount()

    @api.multi
    @api.constrains('to_pay_amount')
    def check_to_pay_amount(self):
        for rec in self:
            # TODO ver si el control lo hacemos por cia o de otra manera
            # only check if invoice has a related transaction, this is more
            # related to demo data
            if rec.transaction_id and (
                    rec.to_pay_amount and rec.currency_id.round(
                    rec.to_pay_amount - rec.amount_total) > 0.0):
                raise ValidationError((
                    'El importe mandado a pagar no puede ser mayor al importe '
                    'de la factura'))

    @api.multi
    def _compute_to_pay_amount(self):
        for rec in self:
            rec.to_pay_amount = rec._get_to_pay_amount_to_date()
            # we force an update of invoice line computed fields
            rec.invoice_line_ids._get_amounts()
            rec.mapped('invoice_line_ids.definitive_line_id')._get_amounts()

    @api.multi
    def _get_to_pay_amount_to_date(self):
        self.ensure_one()
        return True
    # TODO implementar
    # _logger.info('Getting to pay amount for invoice %s' % self.id)
    # # if invoice is paid and not payments, then it is autopaid and after
    # # validation we consider it as send to paid and paid
    # if self.state == 'paid' and not self.payment_ids:
    #     return self.amount_total
    # domain = [
    #     ('move_line_id.move_id', '=', self.move_id.id),
    #     ('amount', '!=', 0),
    #     ('voucher_id.state', 'not in', ('cancel', 'draft'))
    # ]
    # # Add this to allow analysis between dates
    # # from_date = self._context.get('analysis_from_date', False)
    # to_date = self._context.get('analysis_to_date', False)
    # if to_date:
    #     domain += [('voucher_id.confirmation_date', '<=', to_date)]

    # voucher_lines = self.env['account.voucher.line'].search(domain)
    # # si es credito entonces restamos entonces
    # amount = sum(
    #     [x.type == 'dr' and x.amount or -x.amount for x in voucher_lines])
    # if self.type in ('in_refund', 'out_refund'):
    #     amount = -amount
    # return amount

    @api.multi
    def _get_paid_amount_to_date(self):
        self.ensure_one()
        return True
    # TODO implementar
    # _logger.info('Get paid amount to_date for invoice %s' % self.id)
    # to_date = self._context.get('analysis_to_date', False)
    # if not to_date:
    #     return 0.0

    # # if invoice is paid and not payments, then it is autopaid and after
    # # validation we consider it as send to paid and paid
    # if self.state == 'paid' and not self.payment_ids:
    #     return self.amount_total

    # domain = [
    #     ('move_line_id.move_id', '=', self.move_id.id),
    #     ('amount', '!=', 0),
    #     ('voucher_id.state', '=', 'posted')
    # ]
    # if to_date:
    #     domain += [('voucher_id.date', '<=', to_date)]

    # voucher_lines = self.env['account.voucher.line'].search(domain)
    # # si es credito entonces restamos entonces
    # amount = sum(
    #     [x.type == 'dr' and x.amount or -x.amount for x in voucher_lines])
    # if self.type in ('in_refund', 'out_refund'):
    #     amount = -amount
    # return amount

    @api.multi
    @api.constrains('date_invoice', 'invoice_line_ids')
    def check_dates(self):
        _logger.info('Checking invoice dates')
        for rec in self:
            if not rec.date_invoice:
                return True
            for definitive_line in rec.mapped(
                    'invoice_line_ids.definitive_line_id'):
                if rec.date_invoice < definitive_line.issue_date:
                    raise ValidationError(_(
                        'La fecha de la factura no puede ser menor a la fecha '
                        'de la linea definitiva relacionada'))

    @api.multi
    def action_cancel(self):
        for inv in self:
            # if invoice has been send to pay but it is not and advance
            # transaction where they are not actuallly sent to paid, then
            # first you should cancel payment
            if (
                    inv.to_pay_amount and
                    not inv.transaction_id.type_id.with_advance_payment
            ):
                raise ValidationError(_(
                    'You cannot cancel an invoice which has been sent to pay.'
                    ' You need to cancel related payments first.'))
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
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
            raise ValidationError(_(
                'Not Transaction in actual invoice, can not create direct '
                'Payment'))
        res = super(
            AccountInvoice, self).prepare_direct_payment_voucher_vals()
        res['transaction_id'] = self.transaction_id.id
        res['expedient_id'] = self.transaction_id.expedient_id.id
        return res

    @api.multi
    @api.constrains(
        'state',
        'budget_id',
    )
    def check_budget_state_open_pre_closed(self):
        for rec in self:
            if rec.budget_id and rec.budget_id.state not in [
                    'open', 'pre_closed']:
                raise ValidationError(
                    'Solo puede cambiar o registrar comprobantes si '
                    'el presupuesto está abierto o en pre-cierre')

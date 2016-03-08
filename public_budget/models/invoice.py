# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


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
        'Monto Firmado',
        compute='get_signed_amount',
        )
    to_pay_amount = fields.Float(
        string='Monto A Pagar',
        digits=dp.get_precision('Account'),
        compute='_compute_to_pay_amount',
        store=True,
        )

    @api.one
    @api.depends('type', 'amount_total')
    def get_signed_amount(self):
        if self.type in ('in_refund', 'out_refund'):
            signed_amount = -1.0 * self.amount_total
        else:
            signed_amount = self.amount_total
        self.signed_amount = signed_amount

    @api.multi
    def _get_paid_amount_to_date(self):
        self.ensure_one()
        _logger.info('Get paid amount for to_date')
        to_date = self._context.get('analysis_to_date', False)
        if not to_date:
            return 0.0

        # if invoice is paid and not payments, then it is autopaid and after
        # validation we consider it as send to paid and paid
        if self.state == 'paid' and not self.payment_ids:
            return self.amount_total

        domain = [
            ('move_line_id.move_id', '=', self.move_id.id),
            ('amount', '!=', 0),
            ('voucher_id.state', '=', 'posted')
            ]
        if to_date:
            domain += [('voucher_id.date', '<=', to_date)]

        voucher_lines = self.env['account.voucher.line'].search(domain)
        return sum([x.amount for x in voucher_lines])

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
        _logger.info('Getting to pay amount for invoice %s' % self.id)
        # if invoice is paid and not payments, then it is autopaid and after
        # validation we consider it as send to paid and paid
        if self.state == 'paid' and not self.payment_ids:
            self.to_pay_amount = self.amount_total
            return True

        domain = [
            ('move_line_id.move_id', '=', self.move_id.id),
            ('amount', '!=', 0),
            ('voucher_id.state', 'not in', ('cancel', 'draft'))
            ]
        # Add this to allow analysis between dates
        # from_date = self._context.get('analysis_from_date', False)
        to_date = self._context.get('analysis_to_date', False)
        # if from_date:
        #     domain += [('confirmation_date', '>=', from_date)]
        if to_date:
            domain += [('voucher_id.confirmation_date', '<=', to_date)]

        voucher_lines = self.env['account.voucher.line'].search(domain)
        to_pay_amount = sum([x.amount for x in voucher_lines])
        # if invoice is open we ensure that to paid amount is not lower than
        # paid amount
        # we remove this that should works ok without this
        # if self.state in ['open', 'paid']:
        #     paid_amount = self.amount_total - self.residual
        #     if paid_amount > to_pay_amount:
        #         to_pay_amount = paid_amount
        self.to_pay_amount = to_pay_amount

    @api.one
    @api.constrains('date_invoice', 'invoice_line')
    def check_dates(self):
        _logger.info('Checking invoice dates')
        if not self.date_invoice:
            return True
        for definitive_line in self.mapped('invoice_line.definitive_line_id'):
            if self.date_invoice < definitive_line.issue_date:
                raise Warning(_(
                    'La fecha de la factura no puede ser menor a la fecha '
                    'de la linea definitiva relacionada'))

    # we move this to voucher to improove performance
    # @api.one
    # @api.constrains('to_pay_amount', 'amount_total')
    # def check_to_pay_amount(self):
    #     _logger.info('Checking to pay amount on invoice %s' % self.id)
    #     # TODO mejorar, lo hacemos asi por errores de redondeo
    #     if (self.to_pay_amount - self.amount_total) > 0.01:
    #         raise Warning((
    #             'El importe mandado a pagar no puede ser mayor al importe '
    #             'de la factura'))

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

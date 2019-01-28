from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    transaction_id = fields.Many2one(
        'public_budget.transaction',
        copy=False,
        readonly=True,
        auto_join=True,
    )
    budget_id = fields.Many2one(
        related='transaction_id.budget_id',
        readonly=True,
        store=True,
        auto_join=True,
    )
    to_pay_amount = fields.Monetary(
        string='Monto A Pagar',
    )

    @api.multi
    def verify_on_afip(self):
        super(AccountInvoice, self).verify_on_afip()
        return {'type': 'ir.actions.act_window.none'}

    @api.constrains('state')
    def update_definitive_invoiced_amount(self):
        # this method update all amounts on the upstream
        _logger.info('Updating invoice line amounts from invoice')
        for rec in self:
            # if invoice state changes, we recompute to_pay_amount
            rec.sudo()._compute_to_pay_amount()

    @api.constrains('to_pay_amount')
    def check_to_pay_amount(self):
        for rec in self.filtered(lambda x: x.transaction_id and(
            x.to_pay_amount and x.currency_id.round(
                x.to_pay_amount - x.amount_total) > 0.0)):
            raise ValidationError(_(
                'El importe mandado a pagar no puede ser mayor al importe '
                'de la factura'))

    @api.multi
    def _compute_to_pay_amount(self):
        for rec in self:
            rec.to_pay_amount = rec._get_to_pay_amount_to_date()
            # we force an update of invoice line computed fields
            rec.invoice_line_ids._compute_amounts()
            rec.mapped('invoice_line_ids.definitive_line_id')._get_amounts()

    @api.multi
    def _get_to_pay_amount_to_date(self):
        self.ensure_one()
        _logger.info('Getting to pay amount for invoice %s' % self.id)
        # if invoice is paid and not payment group, then it is autopaid or
        # conciliation between account.move.line without a payment group, after
        # validation we consider it as send to paid and paid
        # TODO tal vez deberíamos mejorar porque si estamos sacando
        # analysis_to_date no se estáría teniendo en cuenta
        if self.state == 'paid' and not self.payment_group_ids:
            return self.amount_total

        lines = self.move_id.line_ids.filtered(
            lambda r: r.account_id.internal_type in (
                'payable', 'receivable'))
        domain = [
            ('payment_group_ids.state', 'not in', ['draft', 'cancel']),
            ('id', 'in', lines.ids),
        ]
        # Add this to allow analysis from date
        to_date = self._context.get('analysis_to_date', False)
        if to_date:
            domain += [('payment_group_ids.confirmation_date', '<=', to_date)]

        lines = self.env['account.move.line'].search(domain)
        # en v9+ solo admitimos pago total de facturas por lo cual directamente
        # podemos tomar el importe de la linea (si no habria que ver que parte
        # está vinculada a la orden de pago en la que estamos)
        amount = -sum(lines.mapped('balance'))
        if self.type in ('in_refund', 'out_refund'):
            amount = -amount
        return amount

    @api.multi
    def _get_paid_amount_to_date(self):
        """ Calculo de importe pagado solamente para análisis a fecha ya que
        si no se calcula directamente en las invoiec lines usando el residual
        de las facturas
        """
        self.ensure_one()
        _logger.info('Get paid amount to_date for invoice %s' % self.id)
        to_date = self._context.get('analysis_to_date', False)
        if not to_date:
            return 0.0

        # if invoice is paid and not payment group, then it is autopaid or
        # conciliation between account.move.line without a payment group, after
        # validation we consider it as send to paid and paid
        # TODO tal vez deberíamos mejorar porque si estamos sacando
        # analysis_to_date no se estáría teniendo en cuenta
        if self.state == 'paid' and not self.payment_group_ids:
            return self.amount_total

        lines = self.move_id.line_ids.filtered(
            lambda r: r.account_id.internal_type in (
                'payable', 'receivable'))
        domain = [
            ('payment_group_ids.state', '=', 'posted'),
            ('id', 'in', lines.ids),
        ]
        # Add this to allow analysis from date
        to_date = self._context.get('analysis_to_date', False)
        if to_date:
            domain += [('payment_group_ids.payment_date', '<=', to_date)]

        lines = self.env['account.move.line'].search(domain)
        # en v9+ solo admitimos pago total de facturas por lo cual directamente
        # podemos tomar el importe de la linea (si no habria que ver que parte
        # está vinculada a la orden de pago en la que estamos)
        amount = -sum(lines.mapped('balance'))
        if self.type in ('in_refund', 'out_refund'):
            amount = -amount
        return amount

    @api.constrains('date_invoice', 'invoice_line_ids')
    def check_dates(self):
        _logger.info('Checking invoice dates')
        for rec in self.filtered('date_invoice'):
            for definitive_line in rec.mapped(
                    'invoice_line_ids.definitive_line_id'):
                if rec.date_invoice < definitive_line.issue_date:
                    raise ValidationError(_(
                        'La fecha de la factura no puede ser menor a la fecha '
                        'de la linea definitiva relacionada'))

    @api.multi
    def action_cancel(self):
        for inv in self.filtered(
                lambda x: x.to_pay_amount and
                not x.transaction_id.type_id.with_advance_payment):
            # if invoice has been send to pay but it is not and advance
            # transaction where they are not actuallly sent to paid, then
            # first you should cancel payment
            raise ValidationError(_(
                'You cannot cancel an invoice which has been sent to '
                'pay. You need to cancel related payments first.'))
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for inv in self.filtered(
                lambda x: x.transaction_id.type_id.with_advance_payment):
            # TODO ver si lo borramos, no seria obligatorio que una factura
            # este en el año fiscal del presupuesto ya que puede ser factura
            # de residuo pasivo
            # date = fields.Date.from_string(inv.date)
            # if not inv.budget_id.check_date_in_budget_dates(date):
            #     raise ValidationError((
            #         'La fecha de la factura tiene que estar dentro del año '
            #         'fiscal del presupuesto!'))
            domain = [
                ('move_id', '=', inv.move_id.id),
                ('account_id', '=', inv.account_id.id),
            ]
            move_lines = self.env['account.move.line'].search(domain)
            move_lines.write(
                {'partner_id': self.transaction_id.partner_id.id})
        return res

    @api.constrains(
        'state',
        'budget_id',
    )
    def check_budget_state_open_pre_closed(self):
        for rec in self.filtered(
                lambda x: x.budget_id and x.budget_id.state
                not in ['open', 'pre_closed']):
            raise ValidationError(_(
                'Solo puede cambiar o registrar comprobantes si '
                'el presupuesto está abierto o en pre-cierre'))

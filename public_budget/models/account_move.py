from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):

    _inherit = 'account.move'

    transaction_id = fields.Many2one(
        'public_budget.transaction',
        copy=False,
        readonly=True,
        auto_join=True,
    )
    budget_id = fields.Many2one(
        related='transaction_id.budget_id',
        store=True,
        auto_join=True,
    )
    to_pay_amount = fields.Monetary(
        string='Monto A Pagar',
        compute='_compute_to_pay_amount',
        store=True,
    )

    @api.constrains('to_pay_amount')
    def check_to_pay_amount(self):
        if any(self.filtered(lambda x: x.transaction_id and(
            x.to_pay_amount and x.currency_id.round(
                x.to_pay_amount - x.amount_total) > 0.0))):
            raise ValidationError(_(
                'El importe mandado a pagar no puede ser mayor al importe '
                'de la factura'))

    def l10n_ar_verify_on_afip(self):
        super().l10n_ar_verify_on_afip()
        if self._context.get('from_transaction', 0) == 1:
            action = self.env.ref('account.action_move_in_invoice_type').read()[0]
            action['res_id'] = self.id
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['target'] = 'new'
            return action

    @api.constrains('state')
    def _recompute_to_pay_amount_when_with_advance_payment(self):
        """ Cuando se usan transacciones de tipo con pago de adelanto, por
        alguna razon el metodo _compute_to_pay_amount no se llama cuando se
        pasa la factura a estado pagado, solo se llama cuando pasa a estado
        open, de esta manera reforzamos el re-calculo cuando pasa a pagado
        """
        for rec in self:
            if rec.invoice_payment_state == 'paid' and not rec.payment_group_ids:
                rec._compute_to_pay_amount()

    @api.depends(
        # This do it by a contrains in account payment group
        # 'payment_group_ids.state',
        'state',
    )
    def _compute_to_pay_amount(self):
        _logger.info('Getting to pay amount for invoice %s' % self.ids)
        for rec in self:
            rec.to_pay_amount = rec._get_to_pay_amount_to_date()

    def _get_to_pay_amount_to_date(self):
        """ Para el calculo del mandado a pagar no Podemos usar payment_move_line_ids (campo nativo de odoo que indica
        con que aml se esta pagando la factura) porque solo se setee una vez que exiten los macheos. Nosotros lo
        necesitamos antes, ni bien el payment group esta confirmado
        Por otro lado, en v9+ solo admitimos pago total de facturas y por eso podemos filtrar payment_groups_ids con
        any y ademas podemos directamente  tomar el importe de la linea (si no habria que ver que parte está
        vinculada a la orden de pago en la que estamos)
        """
        self.ensure_one()
        _logger.debug('Get to pay amount to_date for invoice %s' % self.id)
        # if invoice is paid and not payment group, then it is autopaid or
        # conciliation between account.move.line without a payment group,
        # after validation we consider it as send to paid and paid
        # TODO tal vez deberíamos mejorar porque si estamos sacando
        # analysis_to_date no se estáría teniendo en cuenta
        if self.invoice_payment_state == 'paid' and not self.payment_group_ids:
            return self.amount_total

        lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        # Add this to allow analysis from date
        to_date = self._context.get('analysis_to_date', False)
        if to_date:
            to_date = fields.Date.from_string(to_date)
            lines = lines.filtered(lambda x: any(pg.state not in ['draft', 'cancel'] and pg.confirmation_date
                                                 and pg.confirmation_date <= to_date for pg in x.payment_group_ids))
        else:
            lines = lines.filtered(lambda x: any(
                pg.state not in ['draft', 'cancel'] for pg in x.payment_group_ids))
        amount = -sum(lines.mapped('balance'))
        if self.type in ('in_refund', 'out_refund'):
            amount = -amount
        return amount

    def _get_paid_amount_to_date(self):
        """ Calculo de importe pagado solamente para análisis a fecha ya que
        si no se calcula directamente en las invoiec lines usando el residual
        de las facturas.
        Lo hacemos parecido a to_pay pero en relaidad en paid ya tenemos macheo
        y podriamos usar directamente payment_move_line_ids
        """
        self.ensure_one()
        _logger.debug('Get paid amount to_date for invoice %s' % self.id)
        # if invoice is paid and not payment group, then it is autopaid or
        # conciliation between account.move.line without a payment group, after
        # validation we consider it as send to paid and paid
        # TODO tal vez deberíamos mejorar porque si estamos sacando
        # analysis_to_date no se estáría teniendo en cuenta
        if self.invoice_payment_state == 'paid' and not self.payment_group_ids:
            return self.amount_total

        lines = self.line_ids
        # Add this to allow analysis from date
        to_date = self._context.get('analysis_to_date', False)
        if to_date:
            to_date = fields.Date.from_string(to_date)
            lines = lines.filtered(lambda x: any(
                pg.state == 'posted' and pg.payment_date <= to_date for pg in x.payment_group_ids))
        else:
            lines = lines.filtered(lambda x: any(
                pg.state == 'posted' for pg in x.payment_group_ids))

        amount = -sum(lines.mapped('balance'))
        if self.type in ('in_refund', 'out_refund'):
            amount = -amount
        return amount

    @api.constrains('invoice_date', 'invoice_line_ids')
    def check_dates(self):
        _logger.info('Checking invoice dates')
        for rec in self.filtered('invoice_date'):
            for definitive_line in rec.mapped(
                    'invoice_line_ids.definitive_line_id'):
                if rec.invoice_date < definitive_line.issue_date:
                    raise ValidationError(_(
                        'La fecha de la factura no puede ser menor a la fecha '
                        'de la linea definitiva relacionada'))

    def action_cancel(self):
        if self.filtered(
                lambda x: x.to_pay_amount and
                not x.transaction_id.type_id.with_advance_payment):
            # if invoice has been send to pay but it is not and advance
            # transaction where they are not actuallly sent to paid, then
            # first you should cancel payment
            raise ValidationError(_(
                'You cannot cancel an invoice which has been sent to '
                'pay. You need to cancel related payments first.'))
        return super().action_cancel()

    def post(self):
        res = super().post()
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
            move_lines = inv.line_ids.filtered(
                lambda line: line.account_id == inv.transaction_id.type_id.advance_account_id)
            move_lines.write({'partner_id': self.transaction_id.partner_id.id})
        return res

    @api.constrains(
        'state',
        'budget_id',
    )
    def check_budget_state_open_pre_closed(self):
        if self.filtered(
                lambda x: x.budget_id and x.budget_id.state
                not in ['open', 'pre_closed']):
            raise ValidationError(_(
                'Solo puede cambiar o registrar comprobantes si '
                'el presupuesto está abierto o en pre-cierre'))

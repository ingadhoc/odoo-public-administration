# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountInvoiceLine(models.Model):

    _inherit = ['account.invoice.line']

    to_pay_amount = fields.Monetary(
        compute='_get_amounts',
        # store=True,
    )
    paid_amount = fields.Monetary(
        compute='_get_amounts',
        # store=True,
    )
    definitive_line_id = fields.Many2one(
        'public_budget.definitive_line',
        string='Definitive Line',
        readonly=True,
        auto_join=True,
    )

    @api.one
    @api.depends(
        # 'price_subtotal',
        # 'invoice_id.amount_total',
        'invoice_id.residual',
        'invoice_id.to_pay_amount',
    )
    def _get_amounts(self):
        """Update the following fields:
        -to_pay_amount: is the amount of this invoice that is in draft vouchers
        so we consider that is has been sent to be paid. Dividimos
        proporcionalmente por linea, porque sabemos el total a nivel factura
        -paid_amount: vemos el porcentaje que se pago de la factura y,
        al total de cada linea lo multiplicamos por ese porcentaje"""
        _logger.info('Getting amounts for invoice line %s' % self.id)
        invoice_total = self.invoice_id.amount_total
        if invoice_total and self.invoice_id.state not in ('draft', 'cancel'):
            to_date = self._context.get('analysis_to_date', False)
            # if to_date, then we dont get residual from invoice, we get from
            # helper function
            if to_date:
                invoice_paid_perc = (
                    self.invoice_id._get_paid_amount_to_date() / invoice_total)
                invoice_to_pay_perc = (
                    self.invoice_id._get_to_pay_amount_to_date() /
                    invoice_total)
            else:
                # odoo compute residual always positive, no matter invoice
                # is negative
                residual = self.invoice_id.residual
                if invoice_total < 0:
                    residual = -residual
                invoice_paid_perc = (
                    invoice_total - residual) / invoice_total
                invoice_to_pay_perc = (
                    self.invoice_id.to_pay_amount) / invoice_total
            self.to_pay_amount = self.price_subtotal * invoice_to_pay_perc
            self.paid_amount = self.price_subtotal * invoice_paid_perc
        # if someone calls for this recomputation then we call for
        # recomputation on related definitive lines
        # self.definitive_line_id._get_amounts()

    @api.one
    @api.constrains(
        'definitive_line_id',
    )
    def check_budget_state_open_pre_closed(self):
        budget = self.definitive_line_id.budget_id
        if budget and budget.state not in ['open', 'pre_closed']:
            raise ValidationError(_(
                'Solo puede cambiar o registrar comprobantes si '
                'el presupuesto está abierto o en pre-cierre'))

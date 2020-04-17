from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero
import logging
_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    to_pay_amount = fields.Monetary(
        compute='_compute_amounts',
        # store=True,
    )
    paid_amount = fields.Monetary(
        compute='_compute_amounts',
        # store=True,
    )
    definitive_line_id = fields.Many2one(
        'public_budget.definitive_line',
        readonly=True,
        auto_join=True,
    )

    @api.depends(
        # 'price_subtotal',
        'move_id.amount_residual',
        'move_id.to_pay_amount',
    )
    @api.depends_context('analysis_to_date')
    def _compute_amounts(self):
        """Update the following fields:
        -to_pay_amount: is the amount of this invoice that is in draft vouchers
        so we consider that is has been sent to be paid. Dividimos
        proporcionalmente por linea, porque sabemos el total a nivel factura
        -paid_amount: vemos el porcentaje que se pago de la factura y,
        al total de cada linea lo multiplicamos por ese porcentaje"""
        _logger.info('Getting amounts for invoice lines %s' % self.ids)
        to_date = self._context.get('analysis_to_date', False)

        lines = self.filtered(lambda x: x.move_id.state
                              not in ['draft', 'cancel'])

        invoice_vals = {}
        for invoice in lines.mapped('move_id'):
            invoice_total = invoice.amount_total
            # if to_date, then we dont get residual from invoice,
            # we get from helper function
            if to_date:
                invoice_paid_perc = invoice._get_paid_amount_to_date() / invoice_total
                invoice_to_pay_perc = invoice._get_to_pay_amount_to_date() / invoice_total
            else:
                # odoo compute residual always positive, no matter invoice is negative
                residual = invoice.amount_residual
                if invoice_total < 0:
                    residual = -residual
                invoice_paid_perc = (invoice_total - residual) / invoice_total
                invoice_to_pay_perc = invoice.to_pay_amount / invoice_total
            invoice_vals[invoice] = {
                'amount_total': invoice_total,
                'invoice_paid_perc': invoice_paid_perc,
                'invoice_to_pay_perc': invoice_to_pay_perc,
            }
        for rec in lines:
            invoice_total = invoice_vals[rec.move_id]['amount_total']
            if float_is_zero(invoice_total,
                             precision_rounding=rec.currency_id.rounding):
                continue
            rec.to_pay_amount = rec.price_subtotal * \
                invoice_vals[rec.move_id]['invoice_to_pay_perc']
            rec.paid_amount = rec.price_subtotal * \
                invoice_vals[rec.move_id]['invoice_paid_perc']

    @api.constrains(
        'definitive_line_id',
    )
    def check_budget_state_open_pre_closed(self):
        if self.filtered(
                lambda
                x: x.definitive_line_id.
                budget_id and x.definitive_line_id.budget_id.state
                not in ['open', 'pre_closed']):
            raise ValidationError(_(
                'Solo puede cambiar o registrar comprobantes si '
                'el presupuesto está abierto o en pre-cierre'))

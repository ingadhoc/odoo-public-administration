# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class invoice_line(models.Model):
    """"""

    _name = 'account.invoice.line'
    _inherits = {}
    _inherit = ['account.invoice.line']

    to_pay_amount = fields.Float(
        string='To Pay Amount',
        compute='_get_amounts'
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        compute='_get_amounts'
        )
    definitive_line_id = fields.Many2one(
        'public_budget.definitive_line',
        string='Definitive Line',
        readonly=True
        )

    _constraints = [
    ]

    @api.one
    @api.depends(
        'price_subtotal',
        'invoice_id.amount_total',
        'invoice_id.residual')
    def _get_amounts(self):
        """Update the following fields:
        -to_pay_amount: is the amount of this invoice that is in draft vouchers
        so we consider that is has been sent to be paid. Dividimos
        proporcionalmente por linea, porque sabemos el total a nivel factura
        -paid_amount: vemos el porcentaje que se pago de la factura y,
        al total de cada linea lo multiplicamos por ese porcentaje"""
        invoice_total = self.invoice_id.amount_total
        # invoice_paid_perc = 0.0
        # invoice_to_pay_perc = 0.0
        if invoice_total and self.invoice_id.state not in ('draft', 'cancel'):
            invoice_paid_perc = (
                invoice_total - self.invoice_id.residual) / invoice_total
            invoice_to_pay_perc = (
                self.invoice_id.to_pay_amount) / invoice_total
        # TODO implementar to_pay_amount, ver si usamos como hicimos en las
        # preventive lines que lo sacamos de las ordenes de pago o hacemos algo
        # distinto, ver tmb el paid_amount como lo calculamos
            self.to_pay_amount = self.price_subtotal * invoice_to_pay_perc
            self.paid_amount = self.price_subtotal * invoice_paid_perc

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

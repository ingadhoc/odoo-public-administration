# -*- coding: utf-8 -*-
from openerp import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class AccountPaymentGroup(models.Model):

    _inherit = 'account.payment.group'

    cargo_date = fields.Date(
        compute='get_cargo_data',
        string='Fecha del Cargo',
        # necesitamos store para poder ordenarlo
        store=True,
    )
    cargo_amount = fields.Monetary(
        'Cargo',
        help='Cargos Efectuados',
        compute='get_cargo_data',
        store=True,
    )

    @api.one
    @api.depends(
        'payment_date',
        'payments_amount',
        'state',
        'payment_ids.check_ids.amount',
        'payment_ids.check_ids.state',
    )
    def get_cargo_data(self):
        cargo_amount = 0.0
        cargo_date = False
        if self.state == 'posted':
            # al final se valida el pago cuando se entrega y en ese momento
            # se efectua el cargo

            # # si hay cheques, controlamos que esten entregados, si no
            # # tomamos el monto del payment
            # # lo que en v8 era handed y debited, ahora es debited
            # # solamente
            # # ('state', 'in', ['handed', 'debited'])],
            # checks = self.payment_ids.mapped('check_ids')
            # if checks:
            #     # si no estan debitados entonces el monto es cero
            #     debited_checks = checks.filtered(
            #         lambda x: x.state == 'debited')
            #     if debited_checks:
            #         cargo_amount += sum(debited_checks.mapped('amount'))
            #         cargo_date = debited_checks._get_operation(
            #             'debited').date
            # else:
            #     cargo_amount += self.payments_amount
            #     cargo_date = self.payment_date
            cargo_amount += self.payments_amount
            cargo_date = self.payment_date
        self.cargo_date = cargo_date
        self.cargo_amount = cargo_amount

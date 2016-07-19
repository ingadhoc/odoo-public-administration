# -*- coding: utf-8 -*-
from openerp import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class AccountVoucher(models.Model):

    _inherit = 'account.voucher'

    cargo_date = fields.Date(
        compute='get_cargo_data',
        string='Fecha del Cargo',
        # necesitamos store para poder ordenarlo
        store=True,
    )
    cargo_amount = fields.Float(
        'Cargo',
        help='Cargos Efectuados',
        compute='get_cargo_data',
        store=True,
    )

    @api.one
    @api.depends(
        'date',
        'state',
        'amount',
        'issued_check_ids.amount',
        'issued_check_ids.state',
        'issued_check_ids.handed_date'
    )
    def get_cargo_data(self):
        cargo_amount = 0.0
        cargo_date = False
        if self.state == 'posted':
            if self.issued_check_ids:
                # si hay cheques, controlamos que esten entregados, si no
                # tomamos el monto del voucher
                haneded_checks = self.issued_check_ids.search([
                    ('id', 'in', self.issued_check_ids.ids),
                    ('state', 'in', ['handed', 'debited'])],
                    order='handed_date desc')
                cargo_amount += sum(haneded_checks.mapped('amount'))
                cargo_date = haneded_checks and haneded_checks[0].handed_date
            else:
                cargo_amount += self.amount
                cargo_date = self.date
        self.cargo_date = cargo_date
        self.cargo_amount = cargo_amount

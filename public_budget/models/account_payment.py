# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    """"""

    _inherit = 'account.payment'

    # hacemos que la fecha de pago no sea obligatoria ya que seteamos fecha
    # de validacion si no estaba seteada, la setea el payment group
    payment_date = fields.Date(
        required=False,
        default=False,
    )

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        """
        Cambiamos la cuenta que usa el adelanto para utilizar aquella que
        viene de la transaccion de adelanto o del request
        """
        payment_group = self.payment_group_id
        if payment_group.transaction_with_advance_payment:
            account = payment_group.transaction_id.type_id.advance_account_id
            if not account:
                raise ValidationError(_(
                    'In payment of advance transaction type, you need to '
                    'set an advance account in transaction type!'))
            self.destination_account_id = account
        else:
            return super(
                AccountPayment, self)._compute_destination_account_id()

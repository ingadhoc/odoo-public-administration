from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    # hacemos que la fecha de pago no sea obligatoria ya que seteamos fecha
    # de validacion si no estaba seteada, la setea el payment group
    date = fields.Date(
        required=False,
        store=True,
        default=lambda self: fields.Date.today(),
    )

    # para no tener que cambiar tanto el metodo get_period_payments_domain
    # agregamos este campo related
    to_signature_date = fields.Date(
        readonly=False,
    )
    assignee_id = fields.Many2one(
        'res.partner',
        'Cesionario',
        # states={'draft': [('readonly', False)]},
    )
    return_payment_id = fields.Many2one(
        'account.payment',
        string='Línea de devolución',
        readonly=True,
        help='Pago con el que este pago fue devuelto',
    )
    # En realidad la relación es o2o pero no existe en odoo
    returned_payment_ids = fields.One2many(
        'account.payment',
        'return_payment_id',
        help='Pago al que devuelve',
    )

    def write(self, vals):
        """ para pagos que son devolución no dejamos cambiar nada salvo algunos
        campos que se setean a mano
        """
        ok_fields = [
            'receiptbook_id', 'state', 'date',
            'name', 'move_name']
        if not set(ok_fields).intersection(vals.keys()) and self.filtered(
                'returned_payment_ids'):
            raise ValidationError(_(
                'No puede modificar una devolución de retención'))
        return super(AccountPayment, self).write(vals)

    @api.depends('move_id', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        """
        Cambiamos la cuenta que usa el adelanto para utilizar aquella que
        viene de la transaccion de adelanto o del request
        """
        for rec in self:
            if rec.transaction_with_advance_payment:
                account = rec.transaction_id.type_id.advance_account_id
                if not account:
                    raise ValidationError(_(
                        'In payment of advance transaction type, you need to '
                        'set an advance account in transaction type!'))
                rec.destination_account_id = account
            elif rec.advance_request_id:
                rec.destination_account_id = rec.advance_request_id.type_id.account_id
            else:
                super(AccountPayment, rec)._compute_destination_account_id()

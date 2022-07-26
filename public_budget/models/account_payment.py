from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    # hacemos que la fecha de pago no sea obligatoria ya que seteamos fecha
    # de validacion si no estaba seteada, la setea el payment group
    payment_date = fields.Date(
        required=False,
        default=False,
    )
    # para no tener que cambiar tanto el metodo get_period_payments_domain
    # agregamos este campo related
    to_signature_date = fields.Date(
        related='payment_group_id.to_signature_date',
        readonly=False,
    )
    assignee_id = fields.Many2one(
        'res.partner',
        'Cesionario',
        readonly=True,
        states={'draft': [('readonly', False)]},
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
            'document_number', 'receiptbook_id', 'state', 'payment_date',
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
            payment_group = rec.payment_group_id
            if payment_group.transaction_with_advance_payment:
                account = payment_group.\
                    transaction_id.type_id.advance_account_id
                if not account:
                    raise ValidationError(_(
                        'In payment of advance transaction type, you need to '
                        'set an advance account in transaction type!'))
                rec.destination_account_id = account
            elif payment_group.advance_request_id:
                rec.destination_account_id = payment_group.\
                    advance_request_id.type_id.account_id
            else:
                return super(
                    AccountPayment, rec)._compute_destination_account_id()

    def change_withholding(self):
        """ Arrojamos este error para recordarnos que este metodo se implementa
        en realidad en public_budget_tax_settlement porque necesitamos del
        liquidador para marcar liquidada la devolución
        """
        raise ValidationError(_('No implementado todavía'))

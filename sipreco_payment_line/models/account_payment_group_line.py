from odoo import api, models, fields, _
from odoo.exceptions import ValidationError as UserError
import logging

_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class AccountPaymentGroupLine(models.Model):
    """Extend model account.bank.statement."""
    _name = 'account.payment.group.line'
    _description = 'Account Vouchers Payment Lines'

    payment_group_id = fields.Many2one(
        'account.payment.group',
        required=True,
        ondelete='cascade',
    )
    partner_id = fields.Many2one(
        'res.partner',
        required=True,
    )
    cuit = fields.Char(
    )
    bank_account_id = fields.Many2one(
        'res.partner.bank',
        domain="[('partner_id', '=', partner_id)]",
    )
    amount = fields.Monetary(
    )
    currency_id = fields.Many2one(
        related='payment_group_id.currency_id',
        readonly=True,
    )

    def refresh_bank_account(self):
        for rec in self:
            banks = self.partner_id.bank_ids
            if rec.payment_group_id.state == 'posted':
                raise UserError(_(
                    'No se puede cambiar la cuenta de una orden de pago '
                    'validada'))
            rec.bank_account_id = banks and banks[0].id or False

    def _get_linea_archivo_banco(self):
        def only_digits(string):
            return ''.join(filter(lambda x: x.isdigit(), string))

        self.ensure_one()
        # if not self.partner_id.numero_legajo:
        #     UserError(_('El partner %s no tiene número de legajo'))
        numero_legajo = self.partner_id.numero_legajo
        if not numero_legajo:
            raise UserError(_(
                'Se requiere numero de legajo en partner %s') % (
                self.partner_id.name))
        if (
                not self.bank_account_id.acc_number or
                not self.bank_account_id.numero_de_sucursal):
            raise UserError(_(
                'Se requiere cuenta bancaria con número de sucursal.\n'
                '* Partner: %s') % (self.partner_id.name))

        payment_group = self.payment_group_id

        Registro = ""

        # Right("00" & CLng(Sucursal), 2)
        sucursal = self.bank_account_id.numero_de_sucursal.rjust(2, '0')
        if len(sucursal) > 2:
            raise UserError(_(
                'La sucursal de la cuenta bancaria de "%s" no puede tener más '
                'de 2 digitos') % (self.partner_id.name))
        Registro += sucursal

        # Right("00000000" & CLng(Cuenta), 8)
        acc_number = only_digits(self.bank_account_id.acc_number).rjust(8, '0')
        if len(acc_number) > 8:
            raise UserError(_(
                'La cuenta bancaria de "%s" no puede tener más de 8 digitos'
            ) % (self.partner_id.name))
        Registro += acc_number

        Registro += "62"

        # Right("000000" & CLng(Legajo), 6)
        numero_legajo = (only_digits(numero_legajo) or '').rjust(6, '0')
        Registro += numero_legajo[:6]

        # Right("00000000000000" & CLng(Importe * 100), 14)
        Registro += str(int(round(self.amount * 100))).rjust(14, '0')

        # Format(Range("E5").Text, "YYYYMMDD")
        Registro += fields.Date.from_string(
            payment_group.fecha_de_acreditacion).strftime('%Y%m%d')

        Registro += "00"

        Registro += "2"

        Registro += "000000000000"

        # Right("0" & Range("E7").Value, 1)
        Registro += payment_group.tipo_de_pago.rjust(1, '0')

        # Right("000" & Range("E6").Value, 3)
        Registro += payment_group.grupo_asingado_por_bmr.rjust(3, '0')

        Registro += "     "

        Registro += "00000"

        # Right("00000" & Range("E10").Value, 5)
        Registro += payment_group.tipo_de_cuenta.rjust(5, '0')

        # Right("00" & Range("E8").Value, 2)
        Registro += payment_group.sucursal_de_cuenta_debito.rjust(2, '0')

        # Right("00000000" & Range("E9").Value, 8)
        Registro += payment_group.numero_de_cuenta_debito.rjust(8, '0')

        return Registro

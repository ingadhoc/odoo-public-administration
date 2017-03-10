# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError as UserError
import base64


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    payment_line_ids = fields.One2many(
        'account.voucher.payment_line',
        'voucher_id',
        'Payment Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    fecha_de_acreditacion = fields.Date(
        states={'posted': [('readonly', True)]},
    )
    grupo_asingado_por_bmr = fields.Char(
        string='Grupo Asignado por B.M.R.',
        size=2,
        # readonly=True,
        states={'posted': [('readonly', True)]},
    )
    tipo_de_pago = fields.Char(
        size=1,
        states={'posted': [('readonly', True)]},
    )
    sucursal_de_cuenta_debito = fields.Char(
        size=2,
        states={'posted': [('readonly', True)]},
    )
    numero_de_cuenta_debito = fields.Char(
        size=4,
        help='Por ej. 8114',
        states={'posted': [('readonly', True)]},
    )
    tipo_de_cuenta = fields.Char(
        size=1,
        states={'posted': [('readonly', True)]},
    )
    importe_total = fields.Monetary(
        compute='compute_importe_total'
    )
    cantidad = fields.Monetary(
        compute='compute_importe_total'
    )
    archivo_banco = fields.Binary(
        readonly=True
    )
    archivo_banco_name = fields.Char(
        readonly=True,
    )

    @api.one
    @api.depends('payment_line_ids.amount')
    def compute_importe_total(self):
        self.importe_total = sum(self.payment_line_ids.mapped('amount'))
        self.cantidad = len(self.payment_line_ids)

    @api.multi
    def generar_linea(self,):
        self.ensure_one()

    @api.one
    def check_generar_archivo_banco_data(self):
        campos = [
            'fecha_de_acreditacion', 'grupo_asingado_por_bmr',
            'tipo_de_pago', 'sucursal_de_cuenta_debito',
            'numero_de_cuenta_debito', 'tipo_de_cuenta', 'importe_total']
        for field in campos:
            if not self[field]:
                raise UserError(_('Debe definir un valor para el campo %s') % (
                    field))

    @api.one
    def check_payment_lines_total(self):
        if self.importe_total != self.to_pay_amount:
            raise UserError(_(
                'Si existen líneas de pago, el importe a pagar debe ser igual '
                'a la suma de los importes de las líneas de pago'))

    @api.one
    @api.constrains('state')
    def check_confirm_with_payment_lines(self):
        """
        """
        if (
                self.state == 'confirmed' and
                self.type == 'payment' and
                self.payment_line_ids
        ):
            self.check_payment_lines_total()

    @api.one
    def generar_archivo_banco(self):
        self.check_generar_archivo_banco_data()
        lines_data = []
        for line in self.payment_line_ids:
            lines_data.append(line._get_linea_archivo_banco())
        # FOR windows \r\n is required
        # we also add one new line at the end as xls does
        self.archivo_banco = base64.encodestring(
            '\r\n'.join(lines_data) + '\r\n')
        self.archivo_banco_name = 'Archivo banco %s.txt' % fields.Date.today()

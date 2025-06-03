import base64

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError as UserError
from odoo.tools import float_is_zero


class AccountPayment(models.Model):
    _inherit = "account.payment"

    line_ids = fields.One2many(
        "account.payment.group.line",
        "payment_id",
        "Transfer Lines",
    )
    fecha_de_acreditacion = fields.Date()
    grupo_asingado_por_bmr = fields.Char(
        string="Grupo Asignado por B.M.R.",
        size=2,
    )
    tipo_de_pago = fields.Char(
        size=1,
    )
    sucursal_de_cuenta_debito = fields.Char(
        size=2,
    )
    numero_de_cuenta_debito = fields.Char(
        size=4,
        help="Por ej. 8114",
    )
    tipo_de_cuenta = fields.Char(
        size=1,
    )
    importe_total = fields.Monetary(
        compute="_compute_importe_total",
    )
    cantidad = fields.Monetary(
        compute="_compute_importe_total",
    )
    archivo_banco = fields.Binary(readonly=True)
    archivo_banco_name = fields.Char(
        readonly=True,
    )

    @api.depends("line_ids.amount")
    def _compute_importe_total(self):
        for rec in self:
            rec.update(
                {
                    "importe_total": sum(rec.line_ids.mapped("amount")),
                    "cantidad": len(rec.line_ids),
                }
            )

    def generar_linea(self):
        self.ensure_one()

    def check_generar_archivo_banco_data(self):
        campos = [
            "fecha_de_acreditacion",
            "grupo_asingado_por_bmr",
            "tipo_de_pago",
            "sucursal_de_cuenta_debito",
            "numero_de_cuenta_debito",
            "tipo_de_cuenta",
            "importe_total",
        ]
        for field in campos:
            if not self[field]:
                raise UserError(_("Debe definir un valor para el campo %s") % (field))

    def check_payment_lines_total(self):
        if not float_is_zero(self.importe_total - self.to_pay_amount, precision_rounding=self.currency_id.rounding):
            raise UserError(
                _(
                    "Si existen líneas de transferencia, el importe a pagar debe "
                    "ser igual a la suma de los importes de las líneas de pago"
                )
            )

    @api.constrains("state")
    def check_confirm_with_payment_lines(self):
        for rec in self:
            if rec.state == "confirmed" and rec.partner_type == "supplier" and rec.line_ids:
                rec.check_payment_lines_total()

    def generar_archivo_banco(self):
        self.check_generar_archivo_banco_data()
        lines_data = []
        for line in self.line_ids:
            lines_data.append(line._get_linea_archivo_banco())
        # FOR windows \r\n is required
        # we also add one new line at the end as xls does
        self.archivo_banco = base64.encodestring(("\r\n".join(lines_data) + "\r\n").encode())
        self.archivo_banco_name = "Archivo banco %s.txt" % fields.Date.today()

    def remove_all_transfer_lines(self):
        """Botón usado dentro de una orden de pago en una transacción para que en la solapa 'Líneas de Transferencia' se pueda borrar masivamente todas las trasferencias cuando la orden de pago se encuentra en estado 'Borrador'."""
        if self.state == "draft":
            self.line_ids = False

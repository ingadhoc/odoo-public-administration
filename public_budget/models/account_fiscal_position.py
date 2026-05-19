from odoo import _, api, fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    dont_recompute_withholdings = fields.Boolean(
        string="No recomputar retenciones",
        help="Si está activado, las retenciones no se recalcularán cuando se cambie la posición fiscal en un pago.",
    )

    @api.onchange("dont_recompute_withholdings")
    def _onchange_dont_recompute_withholdings(self):
        if self.dont_recompute_withholdings and not self.env.context.get("is_recipt", False):
            return {
                "warning": {
                    "title": "Atención",
                    "message":
                        "Al activar esta opción, las retenciones no se recalcularán cuando se cambie la posición fiscal en un pago. Asegúrese de manejar las retenciones manualmente en este caso."
                    ,
                }
            }

from odoo import api, fields, models


class AccoutMove(models.Model):
    _inherit = "account.move"

    enable_to_pay = fields.Boolean(
        compute="_compute_matched_to_pay",
    )

    def action_pay_tax_settlement(self):
        self.ensure_one()
        line = self.settled_line_ids.filtered(lambda l: l.tax_state == 'to_pay')[:1]
        return line.action_pay_tax_settlement()

    def _compute_matched_to_pay(self):
        for rec in self:
            rec.enable_to_pay = any(
                x.tax_state == "to_pay" for x in rec.settled_line_ids
            )

    @api.model
    def create(self, values):
        # aparentemente esto lo pusimos para que cuando se crea el asiento de liquidación el asiento quede
        # con partner definido
        res = super().create(values)
        if (
            res.move_type == "entry"
            and not res.partner_id
            and len(res.line_ids.mapped("partner_id")) == 1
        ):
            res.partner_id = res.line_ids.mapped("partner_id")
        return res

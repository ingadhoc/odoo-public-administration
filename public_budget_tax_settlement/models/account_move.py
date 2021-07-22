from odoo import api, fields, models, _
from odoo.tools import float_compare


class AccoutMove(models.Model):
    _inherit = 'account.move'

    enable_to_pay = fields.Boolean(
        compute="_compute_matched_to_pay",
    )

    def action_pay_tax_settlement(self):
        self.ensure_one()
        open_move_line_ids = self.line_ids.filtered(
            lambda r: not r.reconciled and r.account_id.internal_type in (
                'payable', 'receivable'))
        return {
            'name': _('Register Payment'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment.group',
            'view_id': False,
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {
                'to_pay_move_line_ids': open_move_line_ids.ids,
                'pop_up': True,
                'default_company_id': self.company_id.id,
                # por defecto, en pago de retenciones, no hacemos double
                # validation
                'force_simple': True,
                # evitamos la restricion de que solo podes agregar pagos en facturas validadas
                'active_model': 'account.payment',
            },
        }

    def _compute_matched_to_pay(self):
        for rec in self:
            rec.enable_to_pay = True if not float_compare(rec._get_cash_basis_matched_percentage(),
                                                          1, precision_digits=5) != -1 else False

    @api.model
    def create(self, values):
        res = super().create(values)
        if res.type == 'entry' and not res.partner_id and len(res.line_ids.mapped('partner_id')) == 1:
            res.partner_id = res.line_ids.mapped('partner_id')
        return res

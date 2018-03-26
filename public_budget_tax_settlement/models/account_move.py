# -*- coding: utf-8 -*-
from openerp import api, models


class AccoutMove(models.Model):
    _inherit = 'account.move'

    @api.multi
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
            },
        }

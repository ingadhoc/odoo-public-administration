# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.exceptions import Warning
from openerp import models, api


class account_check_handed_wizard(models.TransientModel):
    _name = 'account.check.handed.wizard'

    @api.multi
    def action_confirm(self):
        self.ensure_one()

        for check in self.env['account.check'].browse(
                self._context.get('active_ids', [])):
            if check.type != 'issue_check':
                raise Warning(
                    'Los cheques seleccionados deben ser "Cheques Propios"')
            if check.state != 'to_be_handed':
                raise Warning(
                    'Los cheques deben estar en estado "Para Ser Entregado"')
            check.signal_workflow('to_be_handed')
        return True

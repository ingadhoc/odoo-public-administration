# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api


class account_check_action(models.TransientModel):
    _inherit = 'account.check.action'

    @api.model
    def get_vals(self, action_type, check, date):
        vals = super(account_check_action, self).get_vals(
            action_type, check, date)
        # we dont want check debit line to be available for import
        vals['debit_line_vals']['exclude_on_statements'] = True
        return vals

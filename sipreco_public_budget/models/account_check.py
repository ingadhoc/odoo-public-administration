# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class account_check(models.Model):

    _inherit = ['account.check']

    state = fields.Selection(
        # selection_add=[('to_be_handed', 'To Be Handed')]
        [
            ('draft', 'Draft'),
            ('holding', 'Holding'),
            ('deposited', 'Deposited'),
            ('to_be_handed', 'To Be Handed'),
            ('handed', 'Handed'),
            ('rejected', 'Rejected'),
            ('debited', 'Debited'),
            ('returned', 'Returned'),
            ('changed', 'Changed'),
            ('cancel', 'Cancel'),
        ]
        )

    @api.multi
    def check_check_cancellation(self):
        for check in self:
            if check.type == 'issue_check' and check.state not in [
                    'draft', 'to_be_handed', 'handed']:
                raise Warning(_(
                    'You can not cancel issue checks in states other than '
                    '"draft or "handed". First try to change check state.'))
            # third checks received
            elif check.type == 'third_check' and check.state not in [
                    'draft', 'holding']:
                raise Warning(_(
                    'You can not cancel third checks in states other than '
                    '"draft or "holding". First try to change check state.'))
            elif check.type == 'third_check' and check.third_handed_voucher_id:
                raise Warning(_(
                    'You can not cancel third checks that are being used on '
                    'payments'))
        return True

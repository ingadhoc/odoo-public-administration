# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import Warning


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def prepare_direct_payment_voucher_vals(self):
        if not self.transaction_id:
            raise Warning(_('Not Transaction in actual invoice, can not create\
             direct Payment'))
        res = super(
            account_invoice, self).prepare_direct_payment_voucher_vals()
        res['transaction_id'] = self.transaction_id.id
        res['expedient_id'] = self.transaction_id.expedient_id.id
        res['budget_id'] = self.budget_id.id
        return res

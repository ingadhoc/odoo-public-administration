# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def verify_on_afip(self):
        super(AccountInvoice, self).verify_on_afip()
        return {'type': 'ir.actions.act_window.none'}

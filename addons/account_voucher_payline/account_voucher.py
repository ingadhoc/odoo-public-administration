# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.osv import fields as old_fields
import openerp

class account_voucher_payline(models.Model):
    _name = "account.voucher.payline"
    _description = "Account Voucher Payline"

    voucher_id = fields.Many2one('account.voucher', 'Voucher', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=True)
    ammount = fields.Float('Amount', required=True)
    # reference = fields.Reference('Reference')
    _columns = {
        'reference': old_fields.reference('Reference', openerp.addons.base.res.res_request.referencable_models),
    }


class account_voucher(models.Model):

    _inherit = "account.voucher"

    payline_ids = fields.One2many(
        'account.voucher.payline',
        'voucher_id', 
        string='Paylines',
        required=False,
        readonly=True,
        states={'draft':[('readonly',False)]})

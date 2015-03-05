# -*- coding: utf-8 -*-
from openerp import models, fields


class account_voucher(models.Model):
    _inherit = "account.voucher"

    state = fields.Selection(
        selection_add=[
            ('confirmed', 'Confirmed'),
        ])
    # TODO Agregar al help
        # help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
        #             \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
        #             \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
        #             \n* The \'Cancelled\' status is used when user cancel voucher.'),
    # partner_id = fields.Many2one('')
    journal_id = fields.Many2one(
        states={'draft': [('readonly', False)],
                'confirmed': [('readonly', False)]})

    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id,
                         partner_id, date, amount, ttype, company_id,
                         context=None):
        if not journal_id:
            return False
        if ids:
            vouchers = self.browse(cr, uid, ids, context=context)
            if vouchers[0].state == 'confirmed':
                journal_pool = self.pool.get('account.journal')
                journal = journal_pool.browse(
                    cr, uid, journal_id, context=context)
                vals = {'value': {}}
                currency_id = False
                if journal.currency:
                    currency_id = journal.currency.id
                else:
                    currency_id = journal.company_id.currency_id.id

                vals['value'].update({
                    'currency_id': currency_id,
                    'payment_rate_currency_id': currency_id,
                })
                return vals
        return super(account_voucher, self).onchange_journal(
            cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date,
            amount, ttype, company_id, context=context)

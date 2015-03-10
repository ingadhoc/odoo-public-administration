# -*- coding: utf-8 -*-
from openerp import models, fields


class account_voucher(models.Model):
    _inherit = "account.voucher"

    state = fields.Selection(
        # selection_add=[('confirmed', 'Confirmed'), # no usamos por el orden
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('proforma', 'Pro-forma'),
            ('posted', 'Posted')
        ])
    journal_id = fields.Many2one(
        # required=False, #por ahora lo dejamos obligatorio
        # journal could be modified on confirmed state
        states={
            'draft': [('readonly', False)],
            'confirmed': [('readonly', False)]}
        )

    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id,
                         partner_id, date, amount, ttype, company_id,
                         context=None):
        if not journal_id:
            return False
        if ids:
            vouchers = self.browse(cr, uid, ids, context=context)
            # si el journal esta confirmado entonces no cambiamos las
            # imputaciones, solo informacion de la moneda. TODO ver que
            # seguramente habria que cambiar las imputaciones si cambia la
            # moneda. Tal vez lo correcto sea elegir la moneda antes, con un
            # campo nuevo y que solo se puedan elegir diarios de esa moneda
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

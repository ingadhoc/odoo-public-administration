# -*- coding: utf-8 -*-
from openerp import models, fields, api


class account_voucher(models.Model):
    """"""

    _name = 'account.voucher'
    _inherits = {}
    _inherit = ['account.voucher']

    type_with_advance_payment = fields.Boolean(
        readonly=True,
        related='transaction_id.type_id.with_advance_payment'
        )
    note = fields.Html(
        string='Note'
        )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transaction'
        )

    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
        compute="_get_partner_ids")

    @api.one
    @api.depends('transaction_id')
    def _get_partner_ids(self):
        self.partner_ids = self.env['res.partner']
        if not self.transaction_id:
            return False
        invoices = self.env['account.invoice'].search(
            [('transaction_id', '=', self.transaction_id.id),
                ('residual', '>', 0.0)])
        partner_ids = [x.partner_id.id for x in invoices]
        if len(set(partner_ids)) == 1:
            self.partner_id = partner_ids[0]
        self.partner_ids = partner_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class invoice(models.Model):
    """"""

    _name = 'account.invoice'
    _inherits = {}
    _inherit = ['account.invoice']

    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='transaction_id'
        )

    _constraints = [
    ]

    @api.multi
    def invoice_validate(self):
        res = super(invoice, self).invoice_validate()
        for inv in self:
            if inv.transaction_id.type_id.with_advance_payment:
                domain = [
                    ('move_id', '=', inv.move_id.id),
                    ('account_id', '=', inv.account_id.id),
                ]
                move_lines = self.env['account.move.line'].search(domain)
                move_lines.write(
                    {'partner_id': self.transaction_id.partner_id.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

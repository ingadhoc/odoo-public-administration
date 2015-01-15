# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class invoice_line(models.Model):
    """"""

    _name = 'account.invoice.line'
    _inherits = {}
    _inherit = ['account.invoice.line']

    to_pay_amount = fields.Float(
        string='To Pay Amount',
        compute='_get_amounts'
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        compute='_get_amounts'
        )
    definitive_line_id = fields.Many2one(
        'public_budget.definitive_line',
        string='Definitive Line',
        readonly=True
        )

    _constraints = [
    ]

    @api.one
    def _get_amounts(self):
        """"""
        parent = super(invoice_line,self)
        result = parent._get_amounts() if hasattr(parent, '_get_amounts') else False
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

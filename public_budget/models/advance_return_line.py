# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class advance_return_line(models.Model):
    """"""

    _name = 'public_budget.advance_return_line'
    _description = 'advance_return_line'

    amount = fields.Float(
        string='Amount',
        required=True,
        digits=dp.get_precision('Account'),
        )
    advance_return_id = fields.Many2one(
        'public_budget.advance_return',
        ondelete='cascade',
        string='advance_return_id',
        required=True
        )
    advance_request_line_id = fields.Many2one(
        'public_budget.advance_request_line',
        string='advance_request_line_id',
        required=True
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class advance_return_line(models.Model):
    """"""

    _name = 'public_budget.advance_return_line'
    _description = 'advance_return_line'

    amount = fields.Float(
        string='Amount',
        required=True
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

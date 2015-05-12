# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class advance_request_line(models.Model):
    """Advance Request Line"""

    _name = 'public_budget.advance_request_line'
    _description = 'Advance Request Line'

    employee_id = fields.Many2one(
        'res.partner',
        string='Employee',
        required=True,
        context={'default_employee': 1},
        domain=[('employee', '=', True)]
        )
    amount = fields.Float(
        string='Amount',
        required=True
        )
    description = fields.Char(
        string='Description',
        required=True
        )
    balance_amount = fields.Float(
        string='Balance Amount',
        compute='_get_amounts'
        )
    returned_amount = fields.Float(
        string='Returned Amount',
        compute='_get_amounts'
        )
    advance_request_id = fields.Many2one(
        'public_budget.advance_request',
        ondelete='cascade',
        string='advance_request_id',
        required=True
        )
    advance_line_ids = fields.One2many(
        'public_budget.advance_return_line',
        'advance_request_line_id',
        string='advance_line_ids'
        )

    @api.one
    @api.depends(
        'amount',
        # TODO completar con el campo o2m que vamos a agregar
        )
    def _get_amounts(self):
        # TODO implementar!
        self.returned_amount = False
        self.balance_amount = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

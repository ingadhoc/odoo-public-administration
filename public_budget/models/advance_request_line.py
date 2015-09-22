# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


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
    requested_amount = fields.Float(
        string='Requested Amount',
        required=True,
        digits=dp.get_precision('Account'),
        )
    description = fields.Char(
        string='Description',
        required=True,
        )
    debt_amount = fields.Float(
        string=_('Debt Amount'),
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        )
    approved_amount = fields.Float(
        string='Approved Amount',
        digits=dp.get_precision('Account'),
        )
    advance_request_id = fields.Many2one(
        'public_budget.advance_request',
        ondelete='cascade',
        string='advance_request_id',
        required=True
        )

    @api.one
    @api.depends(
        'employee_id',
        # TODO completar con el campo o2m que vamos a agregar
        )
    def _get_amounts(self):
        # TODO implementar!
        self.debt_amount = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

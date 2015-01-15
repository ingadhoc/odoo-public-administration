# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class definitive_line(models.Model):
    """Definitive Line"""

    _name = 'public_budget.definitive_line'
    _description = 'Definitive Line'

    issue_date = fields.Date(
        string='Issue Date',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today
        )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        context={'default_supplier': True},
        domain=[('supplier', '=', True)]
        )
    amount = fields.Float(
        string='Amount',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
        )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        readonly=True
        )
    full_imputation = fields.Boolean(
        string='Full Imputation',
        compute='_get_full_imputation'
        )
    residual_amount = fields.Float(
        string='Residual Amount',
        compute='_get_amounts'
        )
    to_pay_amount = fields.Float(
        string='To Pay Amount',
        compute='_get_amounts'
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        compute='_get_amounts'
        )
    invoiced_amount = fields.Float(
        string='Invoiced Amount',
        compute='_get_amounts'
        )
    to_invoice_amount = fields.Float(
        string='To Invoice'
        )
    transaction_id = fields.Many2one(
        comodel_name='public_budget.transaction',
        string='Transaction',
        readonly=True,
        store=True,
        related='preventive_line_id.transaction_id'
        )
    budget_id = fields.Many2one(
        comodel_name='public_budget.budget',
        string='Budget',
        readonly=True,
        store=True,
        related='preventive_line_id.budget_id'
        )
    budget_position_id = fields.Many2one(
        comodel_name='public_budget.budget_position',
        string='Budget Position',
        readonly=True,
        store=True,
        related='preventive_line_id.budget_position_id'
        )
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('invoiced', 'Invoiced')],
        string='State',
        states={'draft': [('readonly', False)]},
        default='draft',
        compute='_get_state'
        )
    preventive_line_id = fields.Many2one(
        'public_budget.preventive_line',
        ondelete='cascade',
        string='Preventive Line',
        required=True
        )
    invoice_line_ids = fields.One2many(
        'account.invoice.line',
        'definitive_line_id',
        string='Invoice Lines',
        readonly=True
        )

    _constraints = [
    ]

    @api.one
    def _get_full_imputation(self):
        """"""
        raise NotImplementedError

    @api.one
    def _get_state(self):
        """"""
        raise NotImplementedError

    @api.one
    def _get_amounts(self):
        """"""
        raise NotImplementedError

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

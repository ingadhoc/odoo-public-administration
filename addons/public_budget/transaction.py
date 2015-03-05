# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class transaction(models.Model):
    """Budget Transaction"""

    _name = 'public_budget.transaction'
    _description = 'Budget Transaction'

    _order = "id desc"

    _states_ = [
        # State machine: untitle
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancel', 'Cancel'),
    ]

    issue_date = fields.Date(
        string='Issue Date',
        track_visibility='always',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
        default=fields.Date.context_today
        )
    name = fields.Char(
        string='Name',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]}
        )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
        default=lambda self: self.env.user
        )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expedient',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
        )
    type_id = fields.Many2one(
        'public_budget.transaction_type',
        string='Type',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
        )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
        states={'draft': [('readonly', False)]}
        )
    invoice_ids = fields.Many2one(
        'account.invoice',
        string='Vouchers',
        readonly=True
        )
    payment_order_ids = fields.Many2one(
        'account.invoice',
        string='Payment Orders',
        readonly=True
        )
    note = fields.Html(
        string='Note'
        )
    type_with_advance_payment = fields.Boolean(
        string='With advance payment?',
        readonly=True,
        related='type_id.with_advance_payment'
        )
    type_with_salary_advance = fields.Boolean(
        string='With salary advance?',
        readonly=True,
        related='type_id.with_salary_advance'
        )
    definitive_line_ids = fields.One2many(
        comodel_name='public_budget.definitive_line',
        inverse_name='transaction_id',
        string='Definitive Lines',
        readonly=True
        )
    supplier_ids = fields.Many2many(
        relation='transaction_res_partner_rel',
        comodel_name='res.partner',
        string='Suppliers',
        store=True,
        compute='_get_suppliers'
        )
    budget_position_ids = fields.Many2many(
        relation='transaction_position_rel',
        comodel_name='public_budget.budget_position',
        string='Related Budget Positions',
        store=True,
        compute='_get_budget_positions'
        )
    advance_preventive_line_ids = fields.One2many(
        comodel_name='public_budget.preventive_line',
        inverse_name='transaction_id',
        string='Advance Preventive Lines',
        readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
        context={'default_advance_line': 1, 'default_preventive_status': 'confirmed', 'advance_line': 1},
        domain=[('advance_line', '=', True)]
        )
    advance_payment_order_ids = fields.One2many(
        comodel_name='payment.order',
        inverse_name='transaction_id',
        string='Payment Orders'
        )
    refund_voucher_count = fields.Integer(
        string='Refund Vouchers',
        compute='_refund_voucher_count'
        )
    payment_order_count = fields.Float(
        string='Payment Orders',
        compute='_payment_order_count'
        )
    preventive_amount = fields.Float(
        string='Preventive Amount',
        compute='_get_amounts'
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        compute='_get_amounts'
        )
    remaining_amount = fields.Float(
        string='Remaining Amount',
        compute='_get_amounts'
        )
    payment_order_amount = fields.Float(
        string='Payment Orderes Amount',
        compute='_get_amounts'
        )
    advance_remaining_amount = fields.Float(
        string='Advance Remaining Amount',
        compute='_get_advance_amounts'
        )
    refund_voucher_amount = fields.Float(
        string='Refound Vouchers Amount',
        compute='_get_advance_amounts'
        )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env['res.company']._company_default_get('public_budget.transaction')
        )
    state = fields.Selection(
        _states_,
        'State',
        default='draft',
        )
    preventive_line_ids = fields.One2many(
        'public_budget.preventive_line',
        'transaction_id',
        string='Preventive Lines',
        readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
        domain=[('advance_line', '=', False)]
        )
    refund_voucher_ids = fields.One2many(
        'account.voucher',
        'transaction_id',
        string='Vouchers',
        context={'default_type': 'receipt'},
        domain=[('type', '=', 'receipt')]
        )
    advance_return_ids = fields.One2many(
        'public_budget.advance_return',
        'transaction_id',
        string='Advance Returns',
        readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]}
        )
    invoice_ids = fields.One2many(
        'account.invoice',
        'transaction_id',
        string='Invoices',
        track_visibility='always',
        readonly=True
        )
    payment_order_ids = fields.One2many(
        'payment.order',
        'transaction_id',
        string='Payment Orders'
        )

    _constraints = [
    ]

    @api.one
    def _get_suppliers(self):
        """"""
        raise NotImplementedError

    @api.one
    def _get_budget_positions(self):
        """"""
        raise NotImplementedError

    @api.one
    def _refund_voucher_count(self):
        """"""
        raise NotImplementedError

    @api.one
    def _payment_order_count(self):
        """"""
        raise NotImplementedError

    @api.one
    def _get_advance_amounts(self):
        """"""
        raise NotImplementedError

    @api.one
    def _get_amounts(self):
        """"""
        raise NotImplementedError

    @api.multi
    def action_cancel_draft(self):
        # go from canceled state to draft state
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

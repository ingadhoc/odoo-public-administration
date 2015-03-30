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
        states={'draft': [('readonly', False)]},
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
    refund_voucher_count = fields.Integer(
        string='Refund Vouchers',
        compute='_refund_voucher_count'
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
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get('public_budget.transaction')
        )
    total = fields.Float(
        string='Total',
        compute='_get_total'
        )
    user_location_ids = fields.Many2many(
        comodel_name='public_budget.location',
        string='User Locations',
        related='user_id.location_ids'
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
        states={'open': [('readonly', False)]},
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
    voucher_ids = fields.One2many(
        'account.voucher',
        'transaction_id',
        string='Payment Orders',
        readonly=True,
        states={'open': [('readonly', False)]}
        )

    _constraints = [
    ]

    @api.one
    @api.depends(
        'preventive_line_ids',
        'preventive_line_ids.definitive_line_ids',
        'preventive_line_ids.definitive_line_ids.supplier_id',
    )
    def _get_suppliers(self):
        definitive_lines = self.env['public_budget.definitive_line'].search(
            [('preventive_line_id.transaction_id', '=', self.id)])
        supplier_ids = [
            x.supplier_id.id for x in definitive_lines]
        self.supplier_ids = self.env['res.partner']
        self.supplier_ids = supplier_ids

    @api.one
    @api.depends(
        'preventive_line_ids',
        'preventive_line_ids.budget_position_id',
    )
    def _get_budget_positions(self):
        self.budget_position_ids = self.env['public_budget.budget_position']
        budget_position_ids = [
            x.budget_position_id.id for x in self.preventive_line_ids]
        self.budget_position_ids = budget_position_ids

    @api.one
    @api.depends('refund_voucher_ids')
    def _refund_voucher_count(self):
        self.refund_voucher_count = len(self.refund_voucher_ids)

    @api.one
    @api.depends(
        'advance_preventive_line_ids',
        'refund_voucher_ids',
        'refund_voucher_ids.state',
        'invoice_ids',
    )
    def _get_advance_amounts(self):
        refund_voucher_amount = sum(
            x.amount for x in self.refund_voucher_ids if x.state == 'posted')
        self.refund_voucher_amount = refund_voucher_amount
        self.advance_remaining_amount = False
        # TODO
        # self.advance_remaining_amount = self.payment_order_amount - \
            # refund_voucher_amount - self.paid_amount

    @api.one
    @api.depends(
        'preventive_line_ids',
        # 'payment_order_ids',
        # 'payment_order_ids.state',
        # 'total',
    )
    def _get_amounts(self):
        preventive_amount = sum([
            preventive.preventive_amount
            for preventive in self.preventive_line_ids])
        # TODO
        # payment_order_amount = sum(
        #     x.total for x in self.payment_order_ids if x.state == 'done')
        # definitive_amount = sum([
        #     preventive.definitive_amount
        #     for preventive in self.preventive_line_ids])
        # invoiced_amount = sum([
        #     preventive.invoiced_amount
        #     for preventive in self.preventive_line_ids])
        # to_pay_amount = sum([
        #     preventive.to_pay_amount
        #     for preventive in self.preventive_line_ids])
        paid_amount = sum([
            preventive.paid_amount for preventive in self.definitive_line_ids])
        # self.remaining_amount = self.total - preventive_amount
        # self.payment_order_amount = payment_order_amount
        self.preventive_amount = preventive_amount
        # self.definitive_amount = definitive_amount
        # self.invoiced_amount = invoiced_amount
        # self.to_pay_amount = to_pay_amount
        self.paid_amount = paid_amount

    @api.one
    @api.depends(
        'preventive_line_ids',
        'preventive_line_ids.preventive_amount',
        )
    def _get_total(self):
        self.total = sum(
            [x.preventive_amount for x in self.preventive_line_ids])

    @api.multi
    def action_cancel_draft(self):
        # go from canceled state to draft state
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

    @api.one
    def check_closure(self):
        # Check preventive lines
        if not self.preventive_line_ids:
                raise Warning(
                    _('To close a transaction there must be at least one preventive line'))

        for line in self.preventive_line_ids:
            if line.preventive_amount != line.definitive_amount or line.preventive_amount != line.invoiced_amount or line.preventive_amount != line.to_pay_amount or line.preventive_amount != line.paid_amount:
                raise Warning(
                    _('To close a transaction, Preventive, Definitive, Invoiced, To Pay and Paid amount must be the same for each line'))

        # Check advance transactions
        if self.type_id.with_advance_payment:
            if self.advance_remaining_amount != 0.0:
                raise Warning(
                    _('To close a transaction with advance payment, Payment Order Amounts - Refund Amounts should be equal to Definitive Amounts'))

# Constraints
    @api.one
    @api.constrains(
        'type_id', 'advance_preventive_line_ids', 'preventive_line_ids')
    def _check_advance_preventive_lines(self):
        if self.type_id.with_advance_payment:
            # payment_order_amount = sum(
                # x.total for x in self.payment_order_ids if x.state == 'done')
            preventive_amount = sum(
                [x.preventive_amount for x in
                    self.preventive_line_ids])
            # if payment_order_amount < preventive_amount:
            #     raise Warning(
            #         _("In transactions with 'Advance Payment', \
            #             Settlement Amount can't be greater than Payment Orders Amount"))

    @api.one
    @api.constrains('preventive_line_ids', 'type_id', 'expedient_id')
    def _check_transaction_type(self):
        if self.type_id.with_amount_restriction:
            restriction = self.env[
                'public_budget.transaction_type_amo_rest'].search(
                [('transaction_type_id', '=', self.type_id.id),
                 ('date', '<=', self.expedient_id.issue_date)],
                order='date desc', limit=1)
            if restriction:
                if restriction.to_amount < self.total or \
                        restriction.from_amount > self.total:
                    raise Warning(
                        _("Total, Type and Date are not compatible with \
                            Transaction Amount Restrictions"))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

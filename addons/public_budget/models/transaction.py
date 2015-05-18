# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


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

    @api.model
    def _get_default_budget(self):
        budgets = self.env['public_budget.budget'].search(
            [('state', '=', 'open')])
        return budgets and budgets[0] or False

    issue_date = fields.Date(
        string='Issue Date',
        track_visibility='always',
        readonly=True,
        required=True,
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
    budget_id = fields.Many2one(
        'public_budget.budget',
        string='Budget',
        required=True,
        default=_get_default_budget,
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('state', '=', 'open')]
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
        string='Invoices',
        readonly=True
        )
    note = fields.Html(
        string='Note'
        )
    type_with_advance_payment = fields.Boolean(
        readonly=True,
        related='type_id.with_advance_payment'
        )
    type_with_salary_advance = fields.Boolean(
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
        states={'open': [('readonly', False)]},
        context={'default_advance_line': 1, 'default_preventive_status': 'confirmed', 'advance_line': 1},
        domain=[('advance_line', '=', True)]
        )
    preventive_amount = fields.Float(
        string='Preventive Amount',
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        )
    definitive_amount = fields.Float(
        string='Definitive Amount',
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        )
    invoiced_amount = fields.Float(
        string='Invoiced Amount',
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        )
    to_pay_amount = fields.Float(
        string='To Pay Amount',
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        )
    to_return_amount = fields.Float(
        string='To Return Amount',
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        )
    advance_amount = fields.Float(
        string='Advance Amount',
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'public_budget.transaction')
        )
    total = fields.Float(
        string='Total',
        compute='_get_total',
        digits=dp.get_precision('Account'),
        )
    user_location_ids = fields.Many2many(
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
        domain=[('type', '=', 'payment')],
        context={'default_type': 'payment'},
        states={'open': [('readonly', False)]},
        )
    # basicamente es el mismo campo de arriba pero lo separamos para poner en
    # otro lugar de la vista
    advance_voucher_ids = fields.One2many(
        'account.voucher',
        'transaction_id',
        string='Advance Payment Orders',
        readonly=True,
        domain=[('type', '=', 'payment')],
        context={'default_type': 'payment'},
        states={'open': [('readonly', False)]},
        )
    advance_return_ids = fields.One2many(
        'public_budget.advance_return',
        'transaction_id',
        string='Advance Returns',
        readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]}
        )

    @api.one
    @api.depends(
        'partner_id',
        'preventive_line_ids.definitive_line_ids.supplier_id',
    )
    def _get_suppliers(self):
        definitive_lines = self.env['public_budget.definitive_line'].search(
            [('preventive_line_id.transaction_id', '=', self.id)])
        supplier_ids = [
            x.supplier_id.id for x in definitive_lines]
        # if self.partner_id:
        #     supplier_ids.append(self.partner_id.id)
        self.supplier_ids = self.env['res.partner']
        self.supplier_ids = supplier_ids

    @api.one
    @api.depends(
        'preventive_line_ids.budget_position_id',
    )
    def _get_budget_positions(self):
        self.budget_position_ids = self.env['public_budget.budget_position']
        budget_position_ids = [
            x.budget_position_id.id for x in self.preventive_line_ids]
        self.budget_position_ids = budget_position_ids

    @api.one
    @api.depends(
        'preventive_line_ids',
        'voucher_ids.state',
    )
    def _get_amounts(self):
        preventive_amount = sum([
            preventive.preventive_amount
            for preventive in self.preventive_line_ids])
        definitive_amount = sum([
            preventive.definitive_amount
            for preventive in self.preventive_line_ids])
        invoiced_amount = sum([
            preventive.invoiced_amount
            for preventive in self.preventive_line_ids])
        to_pay_amount = sum(
            x.to_pay_amount for x in self.voucher_ids if x.state in ['confirmed', 'posted'])
        paid_amount = sum(
            x.amount for x in self.voucher_ids if x.state == 'posted')

        if self.type_id.with_advance_payment:
            advance_amount = sum([
                x.preventive_amount for x in self.advance_preventive_line_ids])
            self.advance_amount = advance_amount
            self.to_return_amount = paid_amount - invoiced_amount
            if self.state in ('draft', 'open'):
                preventive_amount = sum([
                    preventive.preventive_amount
                    for preventive in self.advance_preventive_line_ids])
                definitive_amount = sum([
                    preventive.definitive_amount
                    for preventive in self.advance_preventive_line_ids])
                invoiced_amount = sum([
                    preventive.invoiced_amount
                    for preventive in self.advance_preventive_line_ids])

        self.preventive_amount = preventive_amount
        self.definitive_amount = definitive_amount
        self.invoiced_amount = invoiced_amount
        self.to_pay_amount = to_pay_amount
        self.paid_amount = paid_amount

    @api.one
    @api.depends(
        'preventive_line_ids.preventive_amount',
        )
    def _get_total(self):
        self.total = sum(
            [x.preventive_amount for x in self.preventive_line_ids])

    @api.multi
    def action_cancel_draft(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

    @api.one
    def check_closure(self):
        """ Check preventive lines
        """
        if not self.preventive_line_ids:
                raise Warning(
                    _('To close a transaction there must be at least one preventive line'))

        for line in self.preventive_line_ids:
            if line.preventive_amount != line.definitive_amount or line.preventive_amount != line.invoiced_amount or line.preventive_amount != line.to_pay_amount or line.preventive_amount != line.paid_amount:
                raise Warning(
                    _('To close a transaction, Preventive, Definitive, Invoiced, To Pay and Paid amount must be the same for each line'))

        # Check advance transactions
        if self.type_id.with_advance_payment:
            if self.to_return_amount != 0.0:
                raise Warning(
                    _('To close a transaction with advance payment, Payment Order Amounts - Refund Amounts should be equal to Definitive Amounts'))

# Constraints
    @api.one
    @api.constrains(
        'type_id', 'advance_preventive_line_ids', 'advance_voucher_ids')
    def _check_advance_preventive_lines(self):
        if self.type_id.with_advance_payment:
            not_cancel_amount = sum(
                x.to_pay_amount for x in self.advance_voucher_ids if x.state != 'cancel')
            print 'not_cancel_amount', not_cancel_amount
            print 'self.advance_amount', self.advance_amount
            if not_cancel_amount > self.advance_amount:
                raise Warning(
                    _("In transactions with 'Advance Payment', \
                        Settlement Amount can't be greater than Payment Orders Amount"))

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

    @api.multi
    def action_new_voucher(self):
        '''
        This function returns an action that display a new voucher
        '''
        self.ensure_one()
        action = self.env['ir.model.data'].xmlid_to_object(
            'account_voucher.action_vendor_payment')

        if not action:
            return False

        res = action.read()[0]

        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'account_voucher.view_vendor_payment_form')
        res['views'] = [(form_view_id, 'form')]

        res['context'] = {
            'default_transaction_id': self.id,
            'default_partner_id': self.partner_id and self.partner_id.id or False,
            'default_type': 'payment',
            }
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

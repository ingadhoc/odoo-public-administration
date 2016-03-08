# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


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
        readonly=True,
        required=True,
        default=fields.Date.context_today,
        states={'draft': [('readonly', False)]},
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
        domain="[('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]}
        )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
        states={'draft': [('readonly', False)]}
        )
    note = fields.Html(
        string='Note'
        )
    type_with_advance_payment = fields.Boolean(
        readonly=True,
        related='type_id.with_advance_payment'
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
        string=_('Suppliers'),
        store=True,
        compute='_get_suppliers'
        )
    budget_position_ids = fields.Many2many(
        relation='transaction_position_rel',
        comodel_name='public_budget.budget_position',
        string=_('Related Budget Positions'),
        store=True,
        compute='_get_budget_positions'
        )
    advance_preventive_line_ids = fields.One2many(
        comodel_name='public_budget.preventive_line',
        inverse_name='transaction_id',
        string=_('Advance Preventive Lines'),
        readonly=True,
        states={'open': [('readonly', False)]},
        context={
            'default_advance_line': 1,
            'default_preventive_status': 'confirmed',
            'advance_line': 1},
        domain=[('advance_line', '=', True)]
        )
    preventive_amount = fields.Float(
        string='Monto Preventivo',
        compute='_get_preventive_amount',
        digits=dp.get_precision('Account'),
        store=True,
        )
    definitive_amount = fields.Float(
        string='Monto Definitivo',
        compute='_get_definitive_amount',
        digits=dp.get_precision('Account'),
        store=True,
        )
    invoiced_amount = fields.Float(
        string='Monto Devengado',
        compute='_get_invoiced_amount',
        digits=dp.get_precision('Account'),
        store=True,
        )
    to_pay_amount = fields.Float(
        string='Monto A Pagar',
        compute='_get_to_pay_amount',
        digits=dp.get_precision('Account'),
        store=True,
        )
    paid_amount = fields.Float(
        string=_('Monto Pagado'),
        compute='_get_paid_amount',
        digits=dp.get_precision('Account'),
        store=True,
        )
    advance_preventive_amount = fields.Float(
        string=_('Monto Preventivo de Adelanto'),
        compute='_get_advance_preventive_amount',
        digits=dp.get_precision('Account'),
        store=True,
        )
    advance_to_pay_amount = fields.Float(
        string=_('Monto de Adelanto a Pagar'),
        compute='_get_advance_amounts',
        digits=dp.get_precision('Account'),
        store=True,
        )
    advance_paid_amount = fields.Float(
        string=_('Monto de Adelanto Pagado'),
        compute='_get_advance_amounts',
        digits=dp.get_precision('Account'),
        store=True,
        )
    advance_remaining_amount = fields.Float(
        string=_('Monto Remanente de Adelanto'),
        compute='_get_advance_remaining_amount',
        digits=dp.get_precision('Account'),
        store=True,
        )
    advance_to_return_amount = fields.Float(
        string=_('Monto a Devolver'),
        compute='_get_advance_to_return_amount',
        digits=dp.get_precision('Account'),
        store=True,
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
        readonly=True,
        states={'open': [('readonly', False)]}
        )
    voucher_ids = fields.One2many(
        'account.voucher',
        'transaction_id',
        string='Payment Orders',
        readonly=True,
        context={'default_type': 'payment'},
        states={'open': [('readonly', False)]},
        domain=[
            ('type', '=', 'payment'),
            ('transaction_with_advance_payment', '=', False)
            ],
        )
    # Usamos otro campo por que si no el depends de advance_voucher_ids se
    # toma en cuenta igual que si fuese el de vouchers y necesitamos que sea
    # distinto para que no recalcule tantas veces. Si no la idea sería que
    # sea basicamente es el mismo campo de arriba pero lo separamos para poner
    # en otro lugar de la vista
    advance_voucher_ids = fields.One2many(
        'account.voucher',
        'transaction_id',
        string='Advance Payment Orders',
        readonly=True,
        domain=[
            ('type', '=', 'payment'),
            ('transaction_with_advance_payment', '=', True)
            ],
        context={'default_type': 'payment'},
        states={'open': [('readonly', False)]},
        )

    @api.one
    @api.constrains('type_id', 'company_id')
    def check_type_company(self):
        if self.type_id.company_id != self.company_id:
            raise Warning(_(
                'Company must be the same as Type Company!'))

    @api.one
    @api.depends(
        'partner_id',
        'preventive_line_ids.definitive_line_ids.supplier_id',
    )
    def _get_suppliers(self):
        definitive_lines = self.env['public_budget.definitive_line'].search(
            [('preventive_line_id.transaction_id', '=', self.id)])
        self.supplier_ids = definitive_lines.mapped('supplier_id')

    @api.one
    @api.depends(
        'preventive_line_ids.budget_position_id',
    )
    def _get_budget_positions(self):
        self.budget_position_ids = self.preventive_line_ids.mapped(
            'budget_position_id')

    @api.one
    @api.depends(
        # TODO este depends puede hacer que se recalcule todo al crear un
        # voucher
        'invoiced_amount',
        'advance_paid_amount',
    )
    def _get_advance_to_return_amount(self):
        _logger.info('Getting Transaction Advance To Return Amount')
        self.advance_to_return_amount = (
            self.advance_paid_amount - self.invoiced_amount)

    @api.one
    @api.depends(
        'advance_preventive_line_ids.preventive_amount',
    )
    def _get_advance_preventive_amount(self):
        _logger.info('Getting Transaction Advance Preventive Amount')
        advance_preventive_amount = sum(self.mapped(
            'advance_preventive_line_ids.preventive_amount'))
        self.advance_preventive_amount = advance_preventive_amount

    @api.one
    @api.depends(
        # TODO ver que esto no deberia llamarse tantas veces
        'advance_preventive_amount',
        'advance_to_pay_amount',
    )
    def _get_advance_remaining_amount(self):
        _logger.info('Getting Transaction Advance Remaining Amount')
        self.advance_remaining_amount = (
            self.advance_preventive_amount - self.advance_to_pay_amount)

    @api.one
    @api.depends(
        'advance_voucher_ids.state',
    )
    def _get_advance_amounts(self):
        _logger.info('Getting Transaction Advance Amounts')
        if not self.advance_voucher_ids:
            return False

        domain = [('id', 'in', self.advance_voucher_ids.ids)]
        to_pay_domain = domain + [('state', 'not in', ('cancel', 'draft'))]
        paid_domain = domain + [('state', '=', 'posted')]

        to_date = self._context.get('analysis_to_date', False)
        if to_date:
            to_pay_domain += [('confirmation_date', '<=', to_date)]
            paid_domain += [('date', '<=', to_date)]

        advance_to_pay_amount = sum(
            self.advance_voucher_ids.search(to_pay_domain).mapped(
                'to_pay_amount'))
        advance_paid_amount = sum(
            self.advance_voucher_ids.search(paid_domain).mapped(
                'amount'))
        self.advance_to_pay_amount = advance_to_pay_amount
        self.advance_paid_amount = advance_paid_amount

    @api.multi
    def mass_voucher_create(self):
        self.ensure_one()
        self = self.with_context(transaction_id=self.id)
        vouchers = self.env['account.voucher']
        for invoice in self.invoice_ids.filtered(
                lambda r: r.state == 'open'):
            _logger.info('Mass Create Voucher for invoice %s' % invoice.id)
            invoice_to_pay_amount = invoice.residual - invoice.to_pay_amount
            # exclude invoices that hast been send to paid
            if not invoice_to_pay_amount or invoice_to_pay_amount == 0.0:
                continue
            journal = self.env['account.journal'].search([
                ('company_id', '=', invoice.company_id.id),
                ('type', 'in', ('cash', 'bank'))], limit=1)
            if not journal:
                raise Warning(_(
                    'No bank or cash journal found for company "%s"') % (
                    invoice.company_id.name))
            partner = invoice.partner_id.commercial_partner_id
            voucher_data = vouchers.onchange_partner_id(
                partner.id, journal.id, 0.0,
                invoice.currency_id.id, 'payment', False)
            invoice_move_lines = invoice.move_id.line_id.ids
            # only debit lines
            # line_cr_ids = [
            #     (0, 0, vals) for vals in voucher_data['value'].get(
            #         'line_cr_ids', False) if isinstance(vals, dict)]
            line_dr_ids = []
            for vals in voucher_data['value'].get('line_dr_ids', False):
                if (
                        isinstance(vals, dict) and
                        vals.get('move_line_id') in invoice_move_lines):
                    vals['amount'] = invoice_to_pay_amount
                    vals['reconcile'] = True
                    line_dr_ids.append((0, 0, vals))
            account_id = voucher_data['value'].get('account_id', False)
            voucher_vals = {
                'type': 'payment',
                # 'receiptbook_id': self.budget_id.receiptbook_id.id,
                'expedient_id': self.expedient_id.id,
                'partner_id': partner.id,
                'transaction_id': self.id,
                'journal_id': journal.id,
                'account_id': account_id,
                # 'line_cr_ids': line_cr_ids,
                'line_dr_ids': line_dr_ids,
                }
            vouchers.create(voucher_vals)
        return True

    @api.one
    @api.depends(
        'preventive_line_ids.preventive_amount',
     )
    def _get_preventive_amount(self):
        self.preventive_amount = sum(self.mapped(
            'preventive_line_ids.preventive_amount'))

    @api.one
    @api.depends(
        'preventive_line_ids.definitive_amount',
     )
    def _get_definitive_amount(self):
        self.definitive_amount = sum(self.mapped(
            'preventive_line_ids.definitive_amount'))

    @api.one
    @api.depends(
        'preventive_line_ids.invoiced_amount',
     )
    def _get_invoiced_amount(self):
        self.invoiced_amount = sum(self.mapped(
            'preventive_line_ids.invoiced_amount'))

    @api.one
    @api.depends(
        'preventive_line_ids.to_pay_amount',
     )
    def _get_to_pay_amount(self):
        self.to_pay_amount = sum(self.mapped(
            'preventive_line_ids.to_pay_amount'))

    @api.one
    @api.depends(
        'preventive_line_ids.paid_amount',
     )
    def _get_paid_amount(self):
        self.paid_amount = sum(self.mapped(
            'preventive_line_ids.paid_amount'))

    @api.multi
    def get_invoice_vals(
            self, supplier, journal, invoice_date,
            supplier_invoice_number, inv_lines, advance_account=False):
        self.ensure_one()
        journal_type = journal.type
        if journal_type == 'sale':
            inv_type = 'out_invoice'
        elif journal_type == 'purchase':
            inv_type = 'in_invoice'
        elif journal_type == 'sale_refund':
            inv_type = 'out_refund'
        else:
            inv_type = 'in_refund'

        company = self.env.user.company_id
        partner_data = self.env['account.invoice'].onchange_partner_id(
            inv_type, supplier.id, company_id=company.id)
        periods = self.env['account.period'].find(
            invoice_date)
        if not periods:
            raise Warning(_('Not period found for this date'))
        period_id = periods.id

        if advance_account:
            account_id = advance_account.id
        else:
            account_id = partner_data['value'].get('account_id', False)

        vals = {
            'partner_id': supplier.id,
            'date_invoice': invoice_date,
            'supplier_invoice_number': supplier_invoice_number,
            'invoice_line': [(6, 0, inv_lines.ids)],
            # 'name': invoice.name,
            'type': inv_type,
            'currency_id': (
                journal.currency.id or journal.company_id.currency_id.id),
            'account_id': account_id,
            # 'direct_payment_journal_id': advance_journal_id,
            'journal_id': journal.id,
            # 'currency_id': invoice.currency_id and invoice.currency_id.id,
            'fiscal_position': partner_data['value'].get(
                'fiscal_position', False),
            'payment_term': partner_data['value'].get('payment_term', False),
            'company_id': company.id,
            'transaction_id': self.id,
            'period_id': period_id,
            'partner_bank_id': partner_data['value'].get(
                'partner_bank_id', False),
        }
        return vals

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
                raise Warning(_(
                    'To close a transaction there must be at least one\
                    preventive line'))

        for line in self.preventive_line_ids:
            if (
                    line.preventive_amount != line.definitive_amount) or (
                    line.preventive_amount != line.invoiced_amount) or (
                    line.preventive_amount != line.to_pay_amount) or (
                    line.preventive_amount != line.paid_amount):
                raise Warning(_(
                    'To close a transaction, Preventive, Definitive, Invoiced,\
                    To Pay and Paid amount must be the same for each line'))

        # Check advance transactions
        if self.type_id.with_advance_payment:
            if self.advance_to_return_amount != 0.0:
                raise Warning(_(
                    'To close a transaction to return amount must be 0!\n'
                    '* To return amount = advance paid amount - '
                    'invoiced amount\n'
                    '(%s = %s - %s)' % (
                        self.advance_to_return_amount,
                        self.advance_paid_amount,
                        self.invoiced_amount)))

# Constraints
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
                if restriction.to_amount < self.preventive_amount or \
                        restriction.from_amount > self.preventive_amount:
                    raise Warning(_(
                        "Preventive Total, Type and Date are not compatible "
                        "with Transaction Amount Restrictions"))

# Actions
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

        partner_id = self.partner_id

        res['context'] = {
            'default_transaction_id': self.id,
            'default_partner_id': partner_id and partner_id.id or False,
            'default_type': 'payment',
            }
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

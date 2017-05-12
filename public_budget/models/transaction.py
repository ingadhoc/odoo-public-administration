# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class BudgetTransaction(models.Model):

    _name = 'public_budget.transaction'
    _description = 'Budget Transaction'

    _order = "id desc"

    _states_ = [
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
        readonly=True,
        required=True,
        default=fields.Date.context_today,
        states={'draft': [('readonly', False)]},
    )
    name = fields.Char(
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
        domain=[('state', '=', 'open')],
        auto_join=True,
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
    )
    type_with_advance_payment = fields.Boolean(
        readonly=True,
        related='type_id.with_advance_payment'
    )
    definitive_line_ids = fields.One2many(
        comodel_name='public_budget.definitive_line',
        inverse_name='transaction_id',
        string='Definitive Lines',
        readonly=True,
        auto_join=True,
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
        compute='_get_budget_positions',
        auto_join=True,
    )
    advance_preventive_line_ids = fields.One2many(
        comodel_name='public_budget.preventive_line',
        inverse_name='transaction_id',
        string='Advance Preventive Lines',
        readonly=True,
        states={'open': [('readonly', False)]},
        context={
            'default_advance_line': 1,
            'default_preventive_status': 'confirmed',
            'advance_line': 1},
        domain=[('advance_line', '=', True)],
        auto_join=True,
    )
    preventive_amount = fields.Monetary(
        string='Monto Preventivo',
        compute='_get_preventive_amount',
        store=True,
    )
    preventive_balance = fields.Monetary(
        string='Saldo Preventivo',
        compute='_get_preventive_balance',
        store=True,
        help='Saldo Preventivo',
    )
    definitive_balance = fields.Monetary(
        string='Saldo Definitivo',
        compute='_get_definitive_balance',
        store=True,
        help='Saldo Definitivo',
    )
    definitive_amount = fields.Monetary(
        string='Monto Definitivo',
        compute='_get_definitive_amount',
        store=True,
    )
    invoiced_amount = fields.Monetary(
        string='Monto Devengado',
        compute='_get_invoiced_amount',
        store=True,
    )
    to_pay_amount = fields.Monetary(
        string='Monto A Pagar',
        compute='_get_to_pay_amount',
        store=True,
    )
    paid_amount = fields.Monetary(
        string='Monto Pagado',
        compute='_get_paid_amount',
        store=True,
    )
    advance_preventive_amount = fields.Monetary(
        string='Monto Preventivo de Adelanto',
        compute='_get_advance_preventive_amount',
        store=True,
    )
    advance_to_pay_amount = fields.Monetary(
        string='Monto de Adelanto a Pagar',
        compute='_get_advance_amounts',
        store=True,
    )
    advance_paid_amount = fields.Monetary(
        string='Monto de Adelanto Pagado',
        compute='_get_advance_amounts',
        store=True,
    )
    advance_remaining_amount = fields.Monetary(
        string='Monto Remanente de Adelanto',
        compute='_get_advance_remaining_amount',
        store=True,
    )
    advance_to_return_amount = fields.Monetary(
        string='Monto a Devolver',
        compute='_get_advance_to_return_amount',
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
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True,
    )
    # TODO esto deberia ser computado como en voucher?
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
        auto_join=True,
        states={'open': [('readonly', False)]},
        domain=[('advance_line', '=', False)]
    )
    invoice_ids = fields.One2many(
        'account.invoice',
        'transaction_id',
        string='Invoices',
        readonly=True,
        auto_join=True,
        states={'open': [('readonly', False)]}
    )
    definitive_partner_type = fields.Selection(
        related='type_id.definitive_partner_type'
    )

    # TODO re implementar
    # voucher_ids
    payment_group_ids = fields.One2many(
        'account.payment.group',
        'transaction_id',
        string='Payment Orders',
        readonly=True,
        context={'default_partner_type': 'supplier'},
        states={'open': [('readonly', False)]},
        auto_join=True,
        domain=[
            ('partner_type', '=', 'supplier'),
            ('transaction_with_advance_payment', '=', False)
        ],
    )
    # Usamos otro campo por que si no el depends de advance_voucher_ids se
    # toma en cuenta igual que si fuese el de vouchers y necesitamos que sea
    # distinto para que no recalcule tantas veces. Si no la idea sería que
    # sea basicamente es el mismo campo de arriba pero lo separamos para poner
    # en otro lugar de la vista
    # advance_voucher_ids = fields.One2many(
    advance_payment_group_ids = fields.One2many(
        'account.payment.group',
        'transaction_id',
        string='Advance Payment Orders',
        readonly=True,
        domain=[
            ('partner_type', '=', 'supplier'),
            ('transaction_with_advance_payment', '=', True)
        ],
        context={'default_partner_type': 'supplier'},
        auto_join=True,
        states={'open': [('readonly', False)]},
    )

    @api.multi
    @api.constrains('type_id', 'company_id')
    def check_type_company(self):
        for rec in self:
            if rec.type_id.company_id != rec.company_id:
                raise ValidationError(_(
                    'Company must be the same as Type Company!'))

    @api.multi
    @api.depends(
        'partner_id',
        'preventive_line_ids.definitive_line_ids.supplier_id',
    )
    def _get_suppliers(self):
        for rec in self:
            definitive_lines = rec.env['public_budget.definitive_line'].search(
                [('preventive_line_id.transaction_id', '=', rec.id)])
            rec.supplier_ids = definitive_lines.mapped('supplier_id')

    @api.multi
    @api.depends(
        'preventive_line_ids.budget_position_id',
    )
    def _get_budget_positions(self):
        for rec in self:
            rec.budget_position_ids = rec.preventive_line_ids.mapped(
                'budget_position_id')

    @api.multi
    @api.depends(
        # TODO este depends puede hacer que se recalcule todo al crear un
        # voucher
        'invoiced_amount',
        'advance_paid_amount',
    )
    def _get_advance_to_return_amount(self):
        _logger.info('Getting Transaction Advance To Return Amount')
        for rec in self:
            rec.advance_to_return_amount = (
                rec.advance_paid_amount - rec.invoiced_amount)

    @api.multi
    @api.depends(
        'advance_preventive_line_ids.preventive_amount',
    )
    def _get_advance_preventive_amount(self):
        _logger.info('Getting Transaction Advance Preventive Amount')
        for rec in self:
            advance_preventive_amount = sum(rec.mapped(
                'advance_preventive_line_ids.preventive_amount'))
            rec.advance_preventive_amount = advance_preventive_amount

    @api.multi
    @api.depends(
        # TODO ver que esto no deberia llamarse tantas veces
        'advance_preventive_amount',
        'advance_to_pay_amount',
    )
    def _get_advance_remaining_amount(self):
        _logger.info('Getting Transaction Advance Remaining Amount')
        for rec in self:
            rec.advance_remaining_amount = (
                rec.advance_preventive_amount - rec.advance_to_pay_amount)

    # TODO implementar
    @api.multi
    @api.depends(
        'advance_payment_group_ids.state',
    )
    def _get_advance_amounts(self):
        _logger.info('Getting Transaction Advance Amounts')
        return True
        # if not self.advance_voucher_ids:
        #     return False

        # domain = [('id', 'in', self.advance_voucher_ids.ids)]
        # to_pay_domain = domain + [('state', 'not in', ('cancel', 'draft'))]
        # paid_domain = domain + [('state', '=', 'posted')]

        # to_date = self._context.get('analysis_to_date', False)
        # if to_date:
        #     to_pay_domain += [('confirmation_date', '<=', to_date)]
        #     paid_domain += [('date', '<=', to_date)]

        # advance_to_pay_amount = sum(
        #     self.advance_voucher_ids.search(to_pay_domain).mapped(
        #         'to_pay_amount'))
        # advance_paid_amount = sum(
        #     self.advance_voucher_ids.search(paid_domain).mapped(
        #         'amount'))
        # self.advance_to_pay_amount = advance_to_pay_amount
        # self.advance_paid_amount = advance_paid_amount

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
                raise ValidationError(_(
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

    @api.multi
    @api.depends(
        'preventive_line_ids.preventive_amount',
    )
    def _get_preventive_amount(self):
        for rec in self:
            rec.preventive_amount = sum(rec.mapped(
                'preventive_line_ids.preventive_amount'))

    @api.multi
    @api.depends(
        'preventive_amount',
        'definitive_amount',
    )
    def _get_preventive_balance(self):
        for rec in self:
            _logger.info(
                'Getting preventive balance for transaction_id %s' % rec.id)
            rec.preventive_balance = (
                rec.preventive_amount - rec.definitive_amount)

    @api.multi
    @api.depends(
        'definitive_amount',
        'invoiced_amount',
    )
    def _get_definitive_balance(self):
        for rec in self:
            _logger.info(
                'Getting definitive balance for transaction_id %s' % rec.id)
            rec.definitive_balance = (
                rec.definitive_amount - rec.invoiced_amount)

    @api.multi
    @api.depends(
        'preventive_line_ids.definitive_amount',
    )
    def _get_definitive_amount(self):
        for rec in self:
            rec.definitive_amount = sum(rec.mapped(
                'preventive_line_ids.definitive_amount'))

    @api.multi
    @api.depends(
        'preventive_line_ids.invoiced_amount',
    )
    def _get_invoiced_amount(self):
        for rec in self:
            rec.invoiced_amount = sum(rec.mapped(
                'preventive_line_ids.invoiced_amount'))

    @api.multi
    @api.depends(
        'preventive_line_ids.to_pay_amount',
    )
    def _get_to_pay_amount(self):
        for rec in self:
            rec.to_pay_amount = sum(rec.mapped(
                'preventive_line_ids.to_pay_amount'))

    @api.multi
    @api.depends(
        'preventive_line_ids.paid_amount',
    )
    def _get_paid_amount(self):
        for rec in self:
            rec.paid_amount = sum(rec.mapped(
                'preventive_line_ids.paid_amount'))

    @api.multi
    def get_invoice_vals(
            self, supplier, journal, invoice_date, invoice_type,
            inv_lines, document_number=False, document_type=False,
            advance_account=False):
        self.ensure_one()
        company = self.env.user.company_id

        if advance_account:
            account_id = advance_account.id
        else:
            account_id = supplier.property_account_receivable_id.id

        vals = {
            'partner_id': supplier.id,
            'date_invoice': invoice_date,
            'document_number': document_number,
            'document_type_id': document_type and document_type.id or False,
            'invoice_line_ids': [(6, 0, inv_lines.ids)],
            'type': invoice_type,
            'account_id': account_id,
            'journal_id': journal.id,
            'company_id': company.id,
            'transaction_id': self.id,
        }
        return vals

    @api.multi
    def action_cancel_draft(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_open(self):
        self.write({'state': 'open'})
        return True

    @api.multi
    def action_close(self):
        self.write({'state': 'closed'})
        return True

    @api.multi
    def check_closure(self):
        """ Check preventive lines
        """
        for rec in self:
            if not rec.preventive_line_ids:
                raise ValidationError(_(
                    'To close a transaction there must be at least one'
                    ' preventive line'))

            for line in rec.preventive_line_ids:
                if (
                        line.preventive_amount != line.definitive_amount) or (
                        line.preventive_amount != line.invoiced_amount) or (
                        line.preventive_amount != line.to_pay_amount) or (
                        line.preventive_amount != line.paid_amount):
                    raise ValidationError(_(
                        'To close a transaction, Preventive, Definitive, '
                        'Invoiced, To Pay and Paid amount must be the same '
                        'for each line'))

            # Check advance transactions
            if rec.type_id.with_advance_payment:
                if rec.advance_to_return_amount != 0.0:
                    raise ValidationError(_(
                        'To close a transaction to return amount must be 0!\n'
                        '* To return amount = advance paid amount - '
                        'invoiced amount\n'
                        '(%s = %s - %s)' % (
                            rec.advance_to_return_amount,
                            rec.advance_paid_amount,
                            rec.invoiced_amount)))

# Constraints
    @api.multi
    @api.constrains(
        'preventive_amount',
        'type_id',
        'expedient_id')
    def _check_transaction_type(self):
        # solo controlamos si hay lineas preventivas
        for rec in self:
            if rec.preventive_line_ids and rec.type_id.with_amount_restriction:
                rest = rec.env[
                    'public_budget.transaction_type_amo_rest'].search(
                    [('transaction_type_id', '=', rec.type_id.id),
                     ('date', '<=', rec.expedient_id.issue_date)],
                    order='date desc', limit=1)
                if rest:
                    if (
                        (rec.company_id.currency_id.round(
                            rest.to_amount - rec.preventive_amount) < 0) or
                        (rec.company_id.currency_id.round(
                            rest.from_amount - rec.preventive_amount) > 0)):
                        raise ValidationError(_(
                            "Preventive Total, Type and Date are not "
                            "compatible with Transaction Amount Restrictions"))

    @api.multi
    def action_new_payment_group(self):
        '''
        This function returns an action that display a new payment group.
        We dont use action on view because it will open on tree view
        '''
        self.ensure_one()
        action = self.env['ir.model.data'].xmlid_to_object(
            'account_payment_group.action_account_payments_group_payable')

        if not action:
            return False

        res = action.read()[0]

        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'action_account_payments_group_payable.'
            'view_account_payment_group_form')
        res['views'] = [(form_view_id, 'form')]

        partner_id = self.partner_id

        res['context'] = {
            'default_transaction_id': self.id,
            'default_partner_id': partner_id and partner_id.id or False,
            'default_type': 'payment',
        }
        return res

    @api.multi
    def copy(self, default=None):
        res = super(BudgetTransaction, self).copy(default)
        attachments = self.env['ir.attachment'].search(
            [('res_model', '=', 'public_budget.transaction'),
             ('res_id', '=', self.id)])
        for att in attachments:
            att.copy(default={
                'res_id': res.id,
                'name': att.name,
            })
        return res

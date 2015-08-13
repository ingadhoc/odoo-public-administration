# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class account_voucher(models.Model):
    """"""

    _name = 'account.voucher'
    _inherits = {}
    _inherit = ['account.voucher']

    budget_id = fields.Many2one(
        related='transaction_id.budget_id',
        readonly=True,
        store=True,
        )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expedient',
        readonly=True,
        # required=True,
        domain=[('type', '=', 'payment'), ('state', '=', 'open')],
        context={'default_type': 'payment'},
        states={'draft': [('readonly', False)]}
        )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transaction',
        # required=True,
        readonly=True,
        )
    budget_position_ids = fields.Many2many(
        relation='voucher_position_rel',
        comodel_name='public_budget.budget_position',
        string='Related Budget Positions',
        compute='_get_budget_positions_and_invoices'
        )
    invoice_ids = fields.Many2many(
        comodel_name='account.invoice',
        string='Related Invoices',
        compute='_get_budget_positions_and_invoices'
        )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Partners',
        compute='_get_partners'
        )
    partner_id = fields.Many2one(
        domain="[('id', 'in', partner_ids[0][2])]",
        )
    transaction_with_advance_payment = fields.Boolean(
        readonly=True,
        related='transaction_id.type_id.with_advance_payment',
        )

    @api.one
    def _get_budget_positions_and_invoices(self):
        self.invoice_ids = self.line_ids.filtered('amount').mapped(
            'move_line_id.invoice')
        self.budget_position_ids = self.invoice_ids.mapped(
            'invoice_line.definitive_line_id.preventive_line_id.budget_position_id')

    @api.one
    @api.depends(
        'transaction_id',
        )
    def _get_partners(self):
        self.partner_ids = self.env['res.partner']
        partner_ids = []
        if self.transaction_id:
            if self.transaction_id.type_id.with_advance_payment and (
                    self.transaction_id.partner_id):
                partner_ids = [self.transaction_id.partner_id.id]
            else:
                partner_ids = self.transaction_id.supplier_ids
        self.partner_ids = partner_ids

    @api.multi
    def onchange_partner_id(
            self, partner_id, journal_id, amount, currency_id, ttype,
            date, transaction_id=False):
        """
        We add transaction on partner change
        """
        move_lines = self.get_transaction_move_lines(
            ttype, partner_id, transaction_id)

        return super(account_voucher, self.with_context(
            move_line_ids=move_lines.ids)).onchange_partner_id(
            partner_id, journal_id, amount, currency_id, ttype, date)

    @api.model
    def get_transaction_move_lines(self, ttype, partner_id, transaction_id):
        if ttype == 'payment':
            account_type = 'payable'
        else:
            account_type = 'receivable'
        move_lines = self.env['account.move.line'].search([
            ('state', '=', 'valid'),
            ('account_id.type', '=', account_type),
            ('reconcile_id', '=', False),
            ('partner_id', '=', partner_id),
            '|', ('invoice', '=', False),
            ('invoice.transaction_id', '=', transaction_id),
            ])
        return move_lines

    def writeoff_move_line_get(
            self, cr, uid, voucher_id, line_total, move_id, name,
            company_currency, current_currency, context=None):
        """Cambiamos la cuenta que usa el adelanto para utilizar aquella que
        viene de la transaccion de adelanto"""
        res = super(account_voucher, self).writeoff_move_line_get(
            cr, uid, voucher_id, line_total, move_id, name,
            company_currency, current_currency, context=context)
        voucher = self.browse(cr, uid, voucher_id, context=context)

        if res and voucher.transaction_with_advance_payment:
            account = voucher.transaction_id.type_id.advance_account_id
            if not account:
                raise Warning(_(
                    'In payment of advance transaction type, you need to\
                    an advance account in transaction type!'))
            res['account_id'] = account.id
        return res

    @api.one
    @api.constrains('advance_amount', 'transaction_id', 'state')
    def check_voucher_transaction_amount(self):
        """
        """
        if self.transaction_with_advance_payment:
            advance_remaining_amount = (
                self.transaction_id.advance_remaining_amount)
            if advance_remaining_amount < 0.0:
                raise Warning(_(
                    'In advance transactions, payment orders amount (%s) can '
                    'not be greater than transaction advance remaining amount '
                    '(%s)') % (
                    self.advance_amount,
                    advance_remaining_amount + self.advance_amount))


class account_voucher_line(models.Model):
    """"""

    _inherit = 'account.voucher.line'

    @api.one
    @api.constrains('amount_unreconciled', 'amount')
    def check_voucher_transaction_amount(self):
        """
        """
        if self.amount > self.amount_unreconciled:
            raise Warning(_(
                'In each line, Amount can not be greater than Open Balance'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

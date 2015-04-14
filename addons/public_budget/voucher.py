# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class voucher(models.Model):
    """"""

    _name = 'account.voucher'
    _inherits = {}
    _inherit = ['account.voucher']

    @api.model
    def _get_default_budget(self):
        budgets = self.env['public_budget.budget'].search(
            [('state', '=', 'open')])
        return budgets and budgets[0] or False

    budget_id = fields.Many2one(
        'public_budget.budget',
        string='Budget',
        required=True,
        default=_get_default_budget,
        readonly=True,
        domain=[('state', '=', 'open')],
        states={'draft': [('readonly', False)]},
        )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expedient',
        readonly=True,
        required=True,
        domain=[('type', '=', 'payment'), ('state', '=', 'open')],
        context={'default_type': 'payment'},
        states={'draft': [('readonly', False)]}
        )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transaction',
        required=True,
        readonly=True,
        # TODO add domain
        # domain=[('state', '=', 'open')],
        states={'draft': [('readonly', False)]},
        )
    budget_position_ids = fields.Many2many(
        relation='voucher_position_rel',
        comodel_name='public_budget.budget_position',
        string='Related Budget Positions',
        compute='_get_budget_positions'
        )
    # supplier_ids = fields.Many2one(
    #     'public_budget.transaction',
    #     string='Transaction',
    #     # readonly=True,
    #     required=True,
    #     )
    supplier_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Suppliers',
        related='transaction_id.supplier_ids'
        )
    partner_id = fields.Many2one(
        domain="[('id', 'in', supplier_ids[0][2])]",
        )

    _constraints = [
    ]

    @api.one
    def _get_budget_positions(self):
        self.budget_position_ids = self.env['public_budget.budget_position']
        budget_position_ids = []
        for line in self.line_ids:
            if line.amount and line.move_line_id and line.move_line_id.invoice:
                budget_position_ids.extend([
                    x.definitive_line_id.budget_position_id.id for x in line.move_line_id.invoice.invoice_line])
        budget_position_ids = list(set(budget_position_ids))
        self.budget_position_ids = budget_position_ids

    @api.one
    @api.onchange(
        'transaction_id',
        )
    def on_change_transaction(self):
        self.partner_id = self.supplier_ids and self.supplier_ids[0] or False

    @api.multi
    def get_transaction_move_lines(self, ttype, partner_id, transaction_id):
        if ttype == 'payment':
            account_type = 'payable'
        else:
            account_type = 'receivable'
        move_lines = self.env['account.move.line'].search([
            ('state','=','valid'),
            ('account_id.type', '=', account_type),
            ('reconcile_id', '=', False),
            ('partner_id', '=', partner_id),
            ('invoice.transaction_id', '=', transaction_id),
            ])
        return move_lines

    # @api.multi
    # def onchange_partner_id(
    #         self, partner_id, journal_id, amount, currency_id, ttype, date,
    #         transaction_id=False):
    #     # Si viene transacion entonces buscamos los move_lines correspondientes y lo pasamos por contexto
    #     if transaction_id:
    #         self = self.with_context(
    #             move_line_ids=self.get_transaction_move_lines(
    #             ttype, partner_id, transaction_id).ids)
    #     res = super(voucher, self).onchange_partner_id(
    #         partner_id, journal_id, amount, currency_id, ttype, date,)
    #     return res

    # @api.multi
    # def onchange_amount(
    #         self, amount, rate, partner_id, journal_id, currency_id, ttype,
    #         date, payment_rate_currency_id, company_id, transaction_id=False):
    #     if transaction_id:
    #         self = self.with_context(
    #             move_line_ids=self.get_transaction_move_lines(
    #             ttype, partner_id, transaction_id).ids)
    #     res = super(voucher, self).onchange_amount(
    #         amount, rate, partner_id, journal_id, currency_id, ttype, date,
    #         payment_rate_currency_id, company_id)
    #     return res

    # def onchange_journal(
    #         self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date,
    #         amount, ttype, company_id, context=None):
    #     return super(voucher, self).onchange_journal(
    #         cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount,
    #         ttype, company_id, context=context)
    # @api.multi
    # def onchange_journal(
    #         self, journal_id, line_ids, tax_id, partner_id, date, amount,
    #         ttype, company_id):
    #         # ttype, company_id, transaction_id):
    #     # if transaction_id:
    #     #     self = self.with_context(
    #     #         move_line_ids=self.get_transaction_move_lines(
    #     #         ttype, partner_id, transaction_id).ids)
    #     res = super(voucher, self).onchange_journal(
    #         journal_id, line_ids, tax_id, partner_id, date, amount, ttype,
    #         company_id)
    #     return res

    @api.multi
    def recompute_voucher_lines(
            self, partner_id, journal_id, price, currency_id, ttype, date):
        default = super(voucher, self).recompute_voucher_lines(
            partner_id, journal_id, price, currency_id, ttype, date)
        return default
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

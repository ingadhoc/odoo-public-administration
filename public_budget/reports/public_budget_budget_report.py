# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from openerp.addons.public_budget.models.transaction import transaction


class PublicBudgetBudgetReport(models.Model):
    _name = "public_budget.budget.report"
    _description = "Budget Report"
    _auto = False
    # _order = 'date desc'
    # _rec_name = 'date'

    # date = fields.Date(readonly=True, string="Fecha")
    # approval_date = fields.Date(
    #     readonly=True, string="Fecha de Aprobación")
    # confirmation_date = fields.Date(
    #     readonly=True, string="Fecha de Confirmación")
    # employee_id = fields.Many2one(
    #     'res.partner', string='Empleado', readonly=True)
    # amount = fields.Float(string='Monto', readonly=True)
    # # TODO make selection
    # state = fields.Char(string='Estado', readonly=True)
    # direction = fields.Selection(
    #     [('request', 'Solicitud'), ('return', 'Devolución')],
    #     string='Solicitud / Devolución', readonly=True)
    # type_id = fields.Many2one(
    #     'public_budget.advance_request_type',
    #     string='Type',
    # )

    # transaction fields
    budget_id = fields.Many2one(
        'public_budget.budget',
        string='Budget',
        readonly=True,
    )
    transaction_type_id = fields.Many2one(
        'public_budget.transaction_type',
        string='Transaction Type',
        readonly=True,
    )
    transaction_partner_id = fields.Many2one(
        'res.partner',
        string='Transaction Partner',
        readonly=True,
    )
    transaction_state = fields.Selection(
        # 'res.partner',
        transaction._states_,
        readonly=True,
    )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transaction',
        readonly=True,
    )
    transaction_expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Transaction Expedient',
        readonly=True,
    )

    # preventive fields
    affects_budget = fields.Boolean(
        readonly=True,
    )
    advance_line = fields.Boolean(
        readonly=True,
    )
    preventive_amount = fields.Float(
        digits=dp.get_precision('Account'),
        readonly=True,
    )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        readonly=True,
    )

    # definitive fields
    definitive_amount = fields.Float(
        digits=dp.get_precision('Account'),
        readonly=True,
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        readonly=True,
    )
    definitive_date = fields.Date(
        readonly=True,
    )

    # invoice line fields
    invoiced_amount = fields.Float(
        digits=dp.get_precision('Account'),
        readonly=True,
    )

    # invoice fields
    invoice_state = fields.Char(
        readonly=True,
    )
    # invoice fields
    invoice_type = fields.Char(
        readonly=True,
    )

    _depends = {
        'public_budget.definitive_line': [
            'issue_date', 'supplier_id', 'amount',
        ],
        'public_budget.preventive_line': [
            'affects_budget', 'advance_line', 'preventive_amount',
            'budget_position_id',
        ],
        'account.invoice.line': [
            'price_subtotal',
        ],
        'account.invoice': [
            'state', 'type',
        ],
        # 'public_budget.advance_request_line': [
        #     'employee_id', 'approved_amount', 'advance_request_id',
        # ],
        # 'public_budget.advance_return': [
        #     'type_id', 'date', 'state',
        # ],
        # 'public_budget.advance_return_line': [
        #     'employee_id', 'returned_amount', 'advance_return_id',
        # ],
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        query = """
            SELECT
                dl.id as id,
                dl.amount as definitive_amount,
                dl.supplier_id as supplier_id,
                dl.issue_date as definitive_date,
                pl.preventive_amount as preventive_amount,
                pl.advance_line as advance_line,
                pl.budget_position_id as budget_position_id,
                pl.affects_budget as affects_budget,
                tr.budget_id as budget_id,
                tr.type_id as transaction_type_id,
                tr.partner_id as transaction_partner_id,
                tr.state as transaction_state,
                tr.id as transaction_id,
                tr.expedient_id as transaction_expedient_id,
                il.price_subtotal as invoiced_amount,
                iv.state as invoice_state,
                iv.type as invoice_type
                -- TODO filtrar por out_invoice', 'in_refund'
                -- am.date as date,
                -- l.date_maturity as date_maturity,
                -- am.ref as ref,
                -- am.state as move_state,
                -- l.reconcile_id as reconcile_id,
                -- l.reconcile_partial_id as reconcile_partial_id,
                -- l.move_id as move_id,
                -- l.partner_id as partner_id,
                -- am.company_id as company_id,
                -- am.journal_id as journal_id,
                -- p.fiscalyear_id as fiscalyear_id,
                -- am.period_id as period_id,
                -- l.account_id as account_id,
                -- l.analytic_account_id as analytic_account_id,
                -- a.type as type,
                -- a.user_type as account_type,
                -- l.currency_id as currency_id,
                -- l.amount_currency as amount_currency,
                -- pa.user_id as user_id,
                -- coalesce(l.debit, 0.0) - coalesce(l.credit, 0.0) as amount
            FROM
                public_budget_transaction tr
                left join
                public_budget_preventive_line pl on (
                    tr.id = pl.transaction_id)
                left join
                public_budget_budget_position bp on (
                    bp.id = pl.budget_position_id)
                left join
                public_budget_definitive_line dl on (
                    pl.id = dl.preventive_line_id)
                left join
                account_invoice_line il on (
                    dl.id = il.definitive_line_id)
                left join
                account_invoice iv on (
                    iv.id = il.invoice_id)
                -- left join account_move am on (am.id=l.move_id)
                -- left join account_period p on (am.period_id=p.id)
                -- left join res_partner pa on (l.partner_id=pa.id)
            WHERE
                pl.affects_budget = True
                -- AND
                -- iv.state NOT IN ('cancel', 'draft')
        """
        cr.execute("""CREATE or REPLACE VIEW %s as (%s
        )""" % (self._table, query))

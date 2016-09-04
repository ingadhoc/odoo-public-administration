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
    transaction_date = fields.Date(
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
    invoice_type = fields.Char(
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        'Invoice',
        readonly=True,
    )

    # voucher line fields
    # voucher_state = fields.Char(
    #     readonly=True,
    # )
    # voucher_type = fields.Char(
    #     readonly=True,
    # )
    # voucher_id = fields.Many2one(
    #     'account.voucher',
    #     'Voucher',
    #     readonly=True,
    # )
    to_pay_amount = fields.Float(
        digits=dp.get_precision('Account'),
        readonly=True,
    )
    paid_amount = fields.Float(
        digits=dp.get_precision('Account'),
        readonly=True,
    )

    # voucher fields
    voucher_state = fields.Char(
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        'Voucher',
        readonly=True,
    )
    voucher_expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Voucher Expedient',
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
        'account.voucher': [
            'state',
        ],
        'account.voucher.line': [
            'amount',
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
                -- dl.id as id,
                CAST(ROW_NUMBER() OVER (
                    ORDER BY tr.issue_date) AS INTEGER) as id,
                -- definitive amount
                -- dl.amount as definitive_amount,
                CASE
                    WHEN il.price_subtotal IS NOT NULL
                    THEN iv.sign * il.price_subtotal
                    ELSE pl.preventive_amount
                END AS preventive_amount,

                dl.supplier_id as supplier_id,
                dl.issue_date as definitive_date,
                -- por si hay mas de una factura
                -- pl.preventive_amount as preventive_amount,
                COALESCE(iv.sign * il.price_subtotal, pl.preventive_amount) as preventive_amount,
                pl.advance_line as advance_line,
                pl.budget_position_id as budget_position_id,
                pl.affects_budget as affects_budget,
                tr.budget_id as budget_id,
                tr.issue_date as transaction_date,
                tr.type_id as transaction_type_id,
                tr.partner_id as transaction_partner_id,
                tr.state as transaction_state,
                tr.id as transaction_id,
                tr.expedient_id as transaction_expedient_id,
                -- CASE
                --     WHEN iv.type in ('out_invoice', 'in_refund')
                --     THEN -1*price_subtotal
                --     ELSE price_subtotal
                -- END AS invoiced_amount,
                il.price_subtotal * iv.sign as invoiced_amount,
                iv.id as invoice_id,
                iv.state as invoice_state,
                iv.type as invoice_type,
                vo.id as voucher_id,
                vo.state as voucher_state,
                vo.expedient_id as voucher_expedient_id,
                CASE
                    WHEN vo.state not in ('cancel', 'draft')
                    THEN vl.amount * vl.sign
                    ELSE 0
                END AS to_pay_amount,
                CASE
                    WHEN vo.state = 'posted'
                    THEN vl.amount * vl.sign
                    ELSE 0
                END AS paid_amount
                -- vl.amount as to_pay_amount,
                -- vl.amount as paid_amount
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
                    (SELECT
                        *,
                        CASE
                            WHEN type IN ('out_invoice', 'in_refund')
                            THEN 1
                            ELSE -1
                        END AS sign
                    FROM
                        account_invoice
                    ) iv on (
                        iv.id = il.invoice_id)
                -- left join
                -- account_invoice iv on (
                --     iv.id = il.invoice_id)
                -- a los voucher lines les unimos move line para tener move_id
                left join
                    (SELECT
                        vl.id,
                        vl.type,
                        vl.amount,
                        vl.voucher_id,
                        CASE
                            WHEN vl.type = 'dr'
                            THEN 1
                            ELSE -1
                        END AS sign,
                        ml.move_id
                    FROM
                        account_voucher_line vl
                        left join
                        account_move_line ml on (
                            ml.id = vl.move_line_id)
                    ) vl on (
                        iv.move_id = vl.move_id)
                left join
                account_voucher vo on (
                    vo.id = vl.voucher_id)
                -- de los v
                -- left join
                -- account_move_line ml on (
                --     ml.id = vl.move_line_id)
                -- left join
                -- account_voucher_line vl on (
                --     ml.move_id = vl.invoice_id)
                -- left join
                -- account_voucher vo on (
                --     iv.id = il.invoice_id)
                -- left join account_move am on (am.id=l.move_id)
                -- left join account_period p on (am.period_id=p.id)
                -- left join res_partner pa on (l.partner_id=pa.id)
            WHERE
                pl.affects_budget = True
                -- esto lo hacemos en el dominio de la vista
                -- AND
                -- iv.state NOT IN ('cancel', 'draft')
        """
        cr.execute("""CREATE or REPLACE VIEW %s as (%s
        )""" % (self._table, query))

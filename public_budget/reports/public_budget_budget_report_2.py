# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from openerp.addons.public_budget.models.transaction import transaction


class PublicBudgetBudgetReport(models.Model):
    _name = "public_budget.budget.report_2"
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
    preventive_line_id = fields.Many2one(
        'public_budget.preventive_line',
        readonly=True,
        string='Preventive Line',
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
        # vamos anidando querys desde el pago hasta la transaccion
        # si hay importe de, por ejemplo, pago, usamos ese para la facturada
        # eso es porque una linea factura podría habrirse en varios pagos
        # y quedaría duplicado
        pay_query = """
            SELECT
                vo.id as voucher_id,
                vo.state as voucher_state,
                vo.expedient_id as voucher_expedient_id,
                vl.move_id as move_id,
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
            FROM
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
                ) vl
                left join
                account_voucher vo on (
                    vo.id = vl.voucher_id)
            """

        invoice_query = """
            SELECT
                COALESCE(pq.to_pay_amount, il.price_subtotal * iv.sign)
                    as invoiced_amount,
                iv.id as invoice_id,
                iv.state as invoice_state,
                iv.type as invoice_type,
                il.definitive_line_id as definitive_line_id,
                pq.*
            FROM
                account_invoice_line il
            LEFT JOIN
                (SELECT
                    *,
                    CASE
                        WHEN type IN ('out_invoice', 'in_refund')
                        THEN 1
                        ELSE -1
                    END AS sign
                FROM
                    account_invoice) iv on (iv.id = il.invoice_id)
            LEFT JOIN
                (%s) as pq on (iv.move_id = pq.move_id)
            """ % (pay_query)

        definitive_query = """
            SELECT
                COALESCE(iq.invoiced_amount, dl.amount)
                    as definitive_amount,
                dl.supplier_id as supplier_id,
                dl.issue_date as definitive_date,
                dl.preventive_line_id as preventive_line_id,
                iq.*
            FROM
                public_budget_definitive_line dl
            LEFT JOIN
                (%s) as iq on (dl.id = iq.definitive_line_id)
            """ % (invoice_query)

        preventive_query = """
            SELECT
                COALESCE(dq.definitive_amount, pl.preventive_amount)
                    as preventive_amount,
                pl.advance_line as advance_line,
                pl.budget_position_id as budget_position_id,
                pl.affects_budget as affects_budget,
                pl.transaction_id as transaction_id,
                dq.*
            FROM
                public_budget_preventive_line pl
            LEFT JOIN
                (%s) as dq on (pl.id = dq.preventive_line_id)
            """ % (definitive_query)

        transaction_query = """
            SELECT
                CAST(ROW_NUMBER() OVER (
                    ORDER BY tr.issue_date) AS INTEGER) as id,
                tr.budget_id as budget_id,
                tr.issue_date as transaction_date,
                tr.type_id as transaction_type_id,
                tr.partner_id as transaction_partner_id,
                tr.state as transaction_state,
                tr.expedient_id as transaction_expedient_id,
                pq.*
            FROM
                public_budget_transaction tr
            LEFT JOIN
                (%s) as pq on (tr.id = pq.transaction_id)
            """ % (preventive_query)

        cr.execute("""CREATE or REPLACE VIEW %s as (%s
        )""" % (self._table, transaction_query))

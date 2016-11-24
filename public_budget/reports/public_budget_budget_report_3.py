# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from openerp.addons.public_budget.models.transaction import transaction


class PublicBudgetBudgetReport(models.Model):
    _name = "public_budget.budget.report_3"
    _description = "Budget Report"
    _rec_name = "resource"
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

    @api.model
    def _reference_models(self):
        return [
            ('account.voucher', 'Voucher'),
            ('account.invoice', 'Invoice'),
            ('public_budget.definitive_line', 'Definitive Line'),
            ('public_budget.preventive_line', 'Preventive Line'),
        ]

# campos que obtenemos en todas las consultas
    resource = fields.Reference(
        selection='_reference_models',
        string='Recurso',
    )
    model = fields.Char(
        readonly=True,
    )
    res_id = fields.Integer(
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Proveedor/Empleado',
        readonly=True,
    )
    document_number = fields.Char(
        readonly=True,
        help='Por ejemplo numero de orden de pago, numero de factura, etc',
        string='Nro de OP/Comprobante',
    )
    reference = fields.Char(
        readonly=True,
        # help='Por ejemplo numero de orden de pago, numero de factura, etc',
        string='Referencia de OP/Comprobante',
    )
    name = fields.Char(
        readonly=True,
        # help='Por ejemplo numero de orden de pago, numero de factura, etc',
        string='Memoria de OP/Comprobante',
    )
    amount = fields.Float(
        digits=dp.get_precision('Account'),
        readonly=True,
    )
    type = fields.Selection([
        ('1_preventive', 'Preventiva'),
        ('2_definitive', 'Definitiva'),
        ('3_invoiced', 'Devengado'),
        ('4_to_pay', 'A Pagar'),
        ('5_paid', 'Pagado'),
    ],
        readonly=True,
        string='Tipo',
    )

    # transaction fields
    budget_id = fields.Many2one(
        'public_budget.budget',
        string='Presupuesto',
        readonly=True,
    )
    transaction_date = fields.Date(
        readonly=True,
        string='Fecha de Transacción',
    )
    transaction_type_id = fields.Many2one(
        'public_budget.transaction_type',
        string='Tipo de Transacción',
        readonly=True,
    )
    transaction_partner_id = fields.Many2one(
        'res.partner',
        string='Partner de Transacción',
        readonly=True,
    )
    transaction_state = fields.Selection(
        # 'res.partner',
        transaction._states_,
        string='Estado de Transacción',
        readonly=True,
    )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transacción',
        readonly=True,
    )
    transaction_expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expediente de Transacción',
        readonly=True,
    )

    # preventive fields
    affects_budget = fields.Boolean(
        readonly=True,
        string='Afecta Presupuesto',
    )
    advance_line = fields.Boolean(
        readonly=True,
        string='Línea de Adelanto',
    )
    preventive_line_id = fields.Many2one(
        'public_budget.preventive_line',
        readonly=True,
        string='Línea Preventiva',
    )
    # preventive_amount = fields.Float(
    #     digits=dp.get_precision('Account'),
    #     readonly=True,
    # )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Partida Presupuestaria',
        readonly=True,
    )
    assignment_position_id = fields.Many2one(
        'public_budget.budget_position',
        # string='Partida Presupuestaria',
        string='Inciso',
        readonly=True,
    )

    # definitive fields
    # definitive_amount = fields.Float(
    #     digits=dp.get_precision('Account'),
    #     readonly=True,
    # )
    # supplier_id = fields.Many2one(
    #     'res.partner',
    #     string='Supplier',
    #     readonly=True,
    # )
    # definitive_date = fields.Date(
    #     readonly=True,
    # )

    # invoice line fields
    # invoiced_amount = fields.Float(
    #     digits=dp.get_precision('Account'),
    #     readonly=True,
    # )

    # invoice fields
    # invoice_state = fields.Char(
    #     readonly=True,
    # )
    # invoice_type = fields.Char(
    #     readonly=True,
    # )
    # invoice_id = fields.Many2one(
    #     'account.invoice',
    #     'Invoice',
    #     readonly=True,
    # )

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
    # voucher fields
    # voucher_state = fields.Char(
    #     readonly=True,
    # )
    # voucher_id = fields.Many2one(
    #     'account.voucher',
    #     'Voucher',
    #     readonly=True,
    # )
    # voucher_expedient_id = fields.Many2one(
    #     'public_budget.expedient',
    #     string='Voucher Expedient',
    #     readonly=True,
    # )

    _depends = {
        # 'public_budget.definitive_line': [
        #     'issue_date', 'supplier_id', 'amount',
        # ],
        # 'public_budget.preventive_line': [
        #     'affects_budget', 'advance_line', 'preventive_amount',
        #     'budget_position_id',
        # ],
        # 'account.invoice.line': [
        #     'price_subtotal',
        # ],
        # 'account.invoice': [
        #     'state', 'type',
        # ],
        # 'account.voucher': [
        #     'state',
        # ],
        # 'account.voucher.line': [
        #     'amount',
        # ],
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
        """
        hacemos una sucesión de consultas que devuelvan:
        * type:
            * 1_preventive (preventives)
            * 2_definitive (definitives)
            * 3_invoiced (invoice lines con invoices)
            * 4_to_pay (voucher con voucher lines)
            * 5_paid (voucher con voucher lines)
        * amount para cada una
        * preventive_line_id a la que está vinculado

        Además unimos para cada type casos especiales de lineas de adelanto

        Unimos todo eso y le hacemos un select para agregar datos genericos:
        * transaction
        * budget position
        * etc..
        """

        tools.drop_view_if_exists(cr, self._table)

        # consulta que agrega a la de payments el preventive_line_id y ademas
        # reparte el amount
        invoice_for_voucher_query = """
            SELECT
                vl.type,
                vl.model,
                vl.res_id,
                vl.resource,
                vl.document_number,
                vl.reference,
                vl.name,
                vl.partner_id,
                dl.preventive_line_id,
                (il.price_subtotal * vl.amount * iv.sign
                    ) / iv.amount_total as amount
            FROM
                account_invoice_line il
            LEFT JOIN
                (SELECT
                    *,
                    CASE
                        WHEN type IN ('in_invoice', 'out_refund')
                        THEN 1
                        ELSE -1
                    END AS sign
                FROM
                    account_invoice) iv on (iv.id = il.invoice_id)
            LEFT JOIN
                public_budget_definitive_line as dl on (
                    il.definitive_line_id = dl.id )
            RIGHT JOIN
                (%s) as vl on (iv.move_id = vl.move_id)
        """

        # consulta template de voucher que luego aplicamos para obtener
        voucher_template = """
            SELECT
                '%s' as type,
                'account.voucher.line' as model,
                vl.id as res_id,
                CONCAT('account.voucher', ',', CAST(vo.id AS VARCHAR)) as resource,
                vo.force_number as document_number,
                vo.reference as reference,
                vo.name as name,
                -- vo.id as voucher_id,
                -- vo.state as voucher_state,
                -- vo.expedient_id as voucher_expedient_id,
                vl.move_id as move_id,
                vo.partner_id as partner_id,
                vl.amount * vl.sign as amount
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
                LEFT JOIN
                account_voucher vo on (
                    vo.id = vl.voucher_id)
            WHERE
                %s
            """

        # aplicamos la consulta anterior para paid y to_pay
        paid_query = invoice_for_voucher_query % (voucher_template % (
            "5_paid", "vo.state = 'posted'"))
        to_pay_query = invoice_for_voucher_query % (voucher_template % (
            "4_to_pay", "vo.state not in ('cancel', 'draft')"))

        # consulta sobre facturas
        invoice_query = """
            SELECT
                '3_invoiced' as type,
                'account.invoice.line' as model,
                il.id as res_id,
                CONCAT('account.invoice', ',', CAST(iv.id AS VARCHAR)) as resource,
                -- TODO tal vez un join para sacar de document_number de move o
                -- o un or para sacar number si no seteado
                -- iv.afip_document_number as document_number,
                COALESCE(iv.afip_document_number, iv.number) as document_number,
                iv.reference as reference,
                iv.name as name,
                -- iv.id as invoice_id,
                -- iv.state as invoice_state,
                -- iv.type as invoice_type,
                -- il.definitive_line_id as definitive_line_id,
                iv.partner_id as partner_id,
                dl.preventive_line_id as preventive_line_id,
                (il.price_subtotal * iv.sign) as amount
            FROM
                account_invoice_line il
            LEFT JOIN
                public_budget_definitive_line as dl on (
                dl.id = il.definitive_line_id)
            LEFT JOIN
                (SELECT
                    *,
                    CASE
                        WHEN type IN ('out_invoice', 'in_refund')
                        THEN -1
                        ELSE 1
                    END AS sign
                FROM
                    account_invoice) iv on (iv.id = il.invoice_id)
            WHERE
                iv.state not in ('cancel', 'draft')
            """

        # consulta sobre definitivas
        definitive_query = """
            SELECT
                '2_definitive' as type,
                'public_budget.definitive_line' as model,
                dl.id as res_id,
                CONCAT('public_budget.definitive_line', ',', CAST(dl.id AS VARCHAR)) as resource,
                null as document_number,
                null as reference,
                null as name,
                -- dl.supplier_id as supplier_id,
                -- dl.issue_date as definitive_date,
                dl.supplier_id as partner_id,
                dl.preventive_line_id as preventive_line_id,
                dl.amount as amount
            FROM
                public_budget_definitive_line dl
            """

        # consulta sobre preventivas
        preventive_query = """
            SELECT
                '1_preventive' as type,
                'public_budget.preventive_line' as model,
                pl.id as res_id,
                CONCAT('public_budget.preventive_line', ',', CAST(pl.id AS VARCHAR)) as resource,
                null as document_number,
                null as reference,
                null as name,
                0 as partner_id,
                pl.id as preventive_line_id,
                pl.preventive_amount as amount
            FROM
                public_budget_preventive_line pl
            -- WHERE
            --     advance_line = False
            """

        # consulta sobre lineas de adelanto para definir monto preventivo
        advance_preventive = """
            SELECT
                '1_preventive' as type,
                'public_budget.preventive_line' as model,
                pl.id as res_id,
                CONCAT('public_budget.preventive_line', ',', CAST(pl.id AS VARCHAR)) as resource,
                null as document_number,
                null as reference,
                null as name,
                0 as partner_id,
                pl.id as preventive_line_id,
                pl.preventive_amount as amount
            FROM
                public_budget_preventive_line pl
            WHERE
                advance_line = True
            """

        # template sobre vouchers ligados a transacciones de adelanto
        # para definir montos definitivos, devengados, a pagar y pagados segun
        # el estado de los vouchers
        advance_template = """
            SELECT
                '%s' as type,
                'public_budget.preventive_line' as model,
                pl.id as res_id,
                CONCAT('public_budget.preventive_line', ',', CAST(pl.id AS VARCHAR)) as resource,
                null as document_number,
                null as reference,
                null as name,
                0 as partner_id,
                pl.id as preventive_line_id,
                av.advance_amount * (
                    pl.preventive_amount /
                    SUM(preventive_amount) OVER(PARTITION BY pl.transaction_id)
                ) as amount
            FROM
                account_voucher as av
            LEFT JOIN
                public_budget_preventive_line as pl on (
                    pl.transaction_id = av.transaction_id)
            WHERE
                av.transaction_with_advance_payment = True and
                pl.advance_line = True and
                -- TODO aca o en algun lugar por aca hay un error!!!
                %s
                -- av.state not in ('cancel', 'draft')
            """

        # partimos de la la consulta de adelanto preventiva y le vamos
        # uniendo las consultas para las definitivas, devengas y a pagar
        advance_query = advance_preventive
        for affect_type in [
                '2_definitive', '3_invoiced', '4_to_pay']:
            advance_query = "%s UNION %s" % (
                advance_query, advance_template % (
                    affect_type, "av.state not in ('cancel', 'draft')"))

        # unimos consulta de las de adelanto pagadas
        advance_query = "%s UNION %s" % (
            advance_query, advance_template % (
                affect_type, "av.state = 'posted'"))

        query = """
            SELECT
            -- agregamos a la consult acore datos globales de linea preventiva
            -- y lineas definitivas
                CAST(ROW_NUMBER() OVER (ORDER BY query.type) AS INTEGER) as id,
                pl.budget_position_id as budget_position_id,
                pl.transaction_id as transaction_id,
                pl.affects_budget as affects_budget,
                pl.advance_line as advance_line,
                tr.budget_id as budget_id,
                tr.issue_date as transaction_date,
                tr.type_id as transaction_type_id,
                tr.partner_id as transaction_partner_id,
                tr.state as transaction_state,
                tr.expedient_id as transaction_expedient_id,
                bp.assignment_position_id as assignment_position_id,
                query.*
            -- consulta core uniendo todas las lineas
            FROM (
                %s
                UNION
                %s
                UNION
                %s
                UNION
                %s
                UNION
                %s
                UNION
                %s
            ) as query
            LEFT JOIN
                public_budget_preventive_line as pl on (
                    pl.id = query.preventive_line_id)
            LEFT JOIN
                public_budget_transaction as tr on (
                    tr.id = pl.transaction_id)
            LEFT JOIN
                public_budget_budget_position as bp on (
                    pl.budget_position_id = bp.id)
            """ % (
                to_pay_query,
                paid_query,
                invoice_query,
                definitive_query,
                preventive_query,
                advance_query,
        )
        cr.execute("""CREATE or REPLACE VIEW %s as (%s
        )""" % (self._table, query))

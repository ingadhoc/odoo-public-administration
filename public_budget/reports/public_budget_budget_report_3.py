from odoo import tools
from odoo import models, fields, api
from odoo.addons.public_budget.models.transaction import BudgetTransaction


class PublicBudgetBudgetReport(models.Model):
    _name = "public_budget.budget.report_3"
    _description = "Budget Report"
    _rec_name = "resource"
    _auto = False

    @api.model
    def _reference_models(self):
        return [
            ('account.payment.group', 'Pagos'),
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
        BudgetTransaction._states_,
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
    # preventive_amount = fields.Monetary(
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

    def init(self):
        """
        hacemos una sucesión de consultas que devuelvan:
        * type:
            * 1_preventive (preventives)
            * 2_definitive (definitives)
            * 3_invoiced (invoice lines con invoices)
            * 4_to_pay (payment groups)
            * 5_paid (payment groups)
        * amount para cada una
        * preventive_line_id a la que está vinculado

        Además unimos para cada type casos especiales de lineas de adelanto

        Unimos todo eso y le hacemos un select para agregar datos genericos:
        * transaction
        * budget position
        * etc..
        """
        # pylint: disable=E8103
        tools.drop_view_if_exists(self._cr, self._table)

        # consulta que agrega a la de payments el preventive_line_id y ademas
        # reparte el amount

        # TODO falta agregar dodo lo de a pagar, pagado y de lineas de adlanto
        # hay que ver como hacemos la consulta ahora
        # consulta sobre facturas
        invoice_query = """
            SELECT
                '3_invoiced' as type,
                'account.invoice.line' as model,
                il.id as res_id,
                CONCAT('account.invoice', ',', CAST(iv.id AS VARCHAR))
                    as resource,
                -- TODO tal vez un join para sacar de document_number de move o
                -- o un or para sacar number si no seteado
                COALESCE(iv.document_number, iv.number)
                    as document_number,
                iv.reference as reference,
                iv.name as name,
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
                CONCAT('public_budget.definitive_line', ',',
                    CAST(dl.id AS VARCHAR)) as resource,
                null as document_number,
                null as reference,
                null as name,
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
                CONCAT('public_budget.preventive_line', ',',
                    CAST(pl.id AS VARCHAR)) as resource,
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
                # to_pay_query,
                # paid_query,
                invoice_query,
                definitive_query,
                preventive_query,
                # advance_query,
        )
        self._cr.execute("""CREATE or REPLACE VIEW %s as (%s
        )""" % (self._table, query))

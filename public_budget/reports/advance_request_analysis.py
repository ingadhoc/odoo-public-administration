# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields


class AdvanceRequestAnalysis(models.Model):
    _name = "advance.request.analysis"
    _description = "Advance Request Analysis"
    _auto = False
    _order = 'date desc'
    # _rec_name = 'date'

    date = fields.Date(readonly=True, string="Fecha")
    approval_date = fields.Date(
        readonly=True, string="Fecha de Aprobación")
    confirmation_date = fields.Date(
        readonly=True, string="Fecha de Confirmación")
    employee_id = fields.Many2one(
        'res.partner', string='Empleado', readonly=True)
    # TODO agregar currency y transformar a monetary
    amount = fields.Float(string='Monto', readonly=True)
    # TODO make selection
    state = fields.Char(string='Estado', readonly=True)
    direction = fields.Selection(
        [('request', 'Solicitud'), ('return', 'Devolución')],
        string='Solicitud / Devolución', readonly=True)
    type_id = fields.Many2one(
        'public_budget.advance_request_type',
        string='Type',
    )

    _depends = {
        'public_budget.advance_request': [
            'type_id', 'date', 'state',
        ],
        'public_budget.advance_request_line': [
            'employee_id', 'approved_amount', 'advance_request_id',
        ],
        'public_budget.advance_return': [
            'type_id', 'date', 'state',
        ],
        'public_budget.advance_return_line': [
            'employee_id', 'returned_amount', 'advance_return_id',
        ],
    }

    def init(self, cr):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(cr, self._table)
        common_fields = 'date, employee_id, type_id, confirmation_date'
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT %s, rql.id, approved_amount AS amount, state,
            'request' AS direction, approval_date
            FROM public_budget_advance_request_line rql
            INNER JOIN public_budget_advance_request rq
            ON rq.id = rql.advance_request_id
            UNION ALL
            SELECT %s, -rtl.id as id, -returned_amount AS amount, state,
            'return' AS direction, NULL AS approval_date
            FROM public_budget_advance_return_line rtl
            INNER JOIN public_budget_advance_return rt
            ON rt.id = rtl.advance_return_id
            )""" % (
            self._table, common_fields, common_fields))

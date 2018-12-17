# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api, _
from odoo.addons.public_budget.models.transaction import BudgetTransaction


class PublicBudgetBudgetReport(models.Model):
    """ En este directamente usamos las líneas preventivas.
    """
    _name = "public_budget.budget.report_4"
    _description = "Budget Report"
    _rec_name = 'budget_position_id'
    _auto = False

    account_id = fields.Many2one(
        'account.account',
        'Cuenta Contable',
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        readonly=True,
    )
    transaction_expedient_id = fields.Many2one(
        'public_budget.expedient',
        'Expediente de la Transacción',
        readonly=True,
    )
    preventive_amount = fields.Monetary(
        string='Preventivo',
        readonly=True,
    )
    advance_line = fields.Boolean(
        string='Advance Line?',
        readonly=True,
    )
    remaining_amount = fields.Monetary(
        string='Remanente',
        readonly=True,
    )
    definitive_amount = fields.Monetary(
        string='Definitivo',
        readonly=True,
    )
    invoiced_amount = fields.Monetary(
        string='Devengado',
        readonly=True,
    )
    to_pay_amount = fields.Monetary(
        string='A pagar',
        readonly=True,
    )
    paid_amount = fields.Monetary(
        string='Pagado',
        readonly=True,
    )
    state = fields.Selection(
        string='Estado',
        selection=[
            ('draft', _('Draft')),
            ('open', _('Open')),
            ('definitive', _('Definitive')),
            ('invoiced', _('Invoiced')),
            ('closed', _('Closed')),
            ('cancel', _('Cancel'))],
        readonly=True,
    )
    affects_budget = fields.Boolean(
        'Afecta Presupuesto?',
        readonly=True,
    )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        'Transacción',
        readonly=True,
    )
    budget_id = fields.Many2one(
        'public_budget.budget',
        'Presupuesto',
        readonly=True,
    )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Partida Presupuestaria',
        readonly=True,
    )
    assignment_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Inciso',
        readonly=True,
    )
    definitive_partner_type = fields.Selection([
        ('supplier', 'Suppliers'),
        ('subsidy_recipient', 'Subsidy Recipients')],
        string='Tipo de Partner',
        readonly=True,
    )
    transaction_type_id = fields.Many2one(
        'public_budget.transaction_type',
        string='Tipo de Transacción',
        readonly=True,
    )
    transaction_date = fields.Date(
        'Fecha de Transacción',
        readonly=True,
    )
    transaction_state = fields.Selection(
        BudgetTransaction._states_,
        string='Estado de Transacción',
        readonly=True,
    )
    transaction_partner_id = fields.Many2one(
        'res.partner',
        string='Partner de Transacción',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)

        query = """
            SELECT
                pl.id,
                pl.account_id,
                rc.currency_id,
                tr.expedient_id as transaction_expedient_id,
                tr.type_id as transaction_type_id,
                tr.state as transaction_state,
                tr.partner_id as transaction_partner_id,
                tr.issue_date as transaction_date,
                pl.preventive_amount,
                pl.advance_line,
                pl.remaining_amount,
                pl.definitive_amount,
                pl.invoiced_amount,
                pl.to_pay_amount,
                pl.paid_amount,
                pl.state,
                pl.affects_budget,
                pl.transaction_id,
                pl.budget_id,
                pl.budget_position_id,
                tt.definitive_partner_type,
                bp.assignment_position_id
            FROM public_budget_preventive_line as pl
            INNER JOIN
                public_budget_transaction as tr on (
                    tr.id = pl.transaction_id)
            INNER JOIN
                public_budget_transaction_type as tt on (
                    tt.id = tr.type_id)
            INNER JOIN
                public_budget_budget_position as bp on (
                    bp.id = pl.budget_position_id)
            INNER JOIN
                res_company as rc on (
                    rc.id = tr.company_id)
            """
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (
            self._table, query))

from odoo import models, fields


class BudgetPrecloseDetail(models.Model):
    """"""

    _name = 'public_budget.budget_prec_detail'
    _description = 'Budget Preclose Detail'
    _order = "order_int"

    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        required=True
    )
    amount = fields.Monetary(
        readonly=True,
        required=True,
    )
    draft_amount = fields.Monetary(
        readonly=True,
        required=True,
    )
    preventive_amount = fields.Monetary(
        readonly=True,
        required=True,
    )
    definitive_amount = fields.Monetary(
        readonly=True,
        required=True,
    )
    to_pay_amount = fields.Monetary(
        readonly=True,
        required=True,
    )
    paid_amount = fields.Monetary(
        readonly=True,
        required=True,
    )
    balance_amount = fields.Monetary(
        readonly=True,
        required=True,
    )
    account_type = fields.Selection(
        string='Type',
        related='budget_position_id.type',
        readonly=True,
    )
    order_int = fields.Integer(
        string='Parent Left'
    )
    budget_id = fields.Many2one(
        'public_budget.budget',
        required=True
    )
    currency_id = fields.Many2one(
        related='budget_id.company_id.currency_id',
        readonly=True,
    )

# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class BudgetModificationDetail(models.Model):

    _name = 'public_budget.budget_modification_detail'
    _description = 'Budget Modification Detail'

    amount = fields.Monetary(
        string='Amount',
        required=True,
    )
    budget_modification_id = fields.Many2one(
        'public_budget.budget_modification',
        ondelete='cascade',
        string='Modification',
        required=True
    )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        required=True,
        store=True,
        context={
            'default_type': 'normal', 'default_budget_assignment_allowed': 1},
        domain=[('budget_assignment_allowed', '=', True)]
    )
    budget_id = fields.Many2one(
        related='budget_modification_id.budget_id',
        readonly=True,
        store=True,
    )
    currency_id = fields.Many2one(
        related='budget_id.currency_id',
        readonly=True,
    )
    date = fields.Date(
        'Budget Modification Date',
        related='budget_modification_id.date',
        readonly=True,
        store=True
    )
    reference = fields.Char(
        'Budget Modification Reference',
        related='budget_modification_id.reference',
        readonly=True,
    )
    name = fields.Char(
        'Budget Modification Name',
        related='budget_modification_id.name',
        readonly=True,
    )
    type = fields.Selection(
        related='budget_modification_id.type',
        readonly=True,
        store=True,
    )

    @api.multi
    @api.constrains('budget_position_id', 'amount')
    def _check_modification(self):
        for rec in self:
            budget_id = rec.budget_modification_id.budget_id.id
            if rec.budget_position_id.budget_assignment_allowed and (
                    rec.with_context(
                        budget_id=budget_id
                    ).budget_position_id.balance_amount < 0.0):
                raise ValidationError(
                    _("You can not make this modification as '%s' will have a "
                        "negative balance") % (rec.budget_position_id.name))

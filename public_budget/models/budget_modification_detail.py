from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BudgetModificationDetail(models.Model):

    _name = 'public_budget.budget_modification_detail'
    _description = 'Budget Modification Detail'

    amount = fields.Monetary(
        required=True,
    )
    budget_modification_id = fields.Many2one(
        'public_budget.budget_modification',
        ondelete='cascade',
        required=True
    )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        required=True,
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
    def unlink(self):
        to_check = []
        for rec in self:
            to_check.append((
                rec.budget_position_id, rec.budget_modification_id.budget_id))
        res = super(BudgetModificationDetail, self).unlink()
        for position, budget in to_check:
            self._check_modification(position, budget)
        return res

    @api.constrains('budget_position_id', 'amount')
    def check_modification(self):
        for rec in self:
            self._check_modification(
                rec.budget_position_id,
                rec.budget_modification_id.budget_id)

    @api.model
    def _check_modification(self, position, budget):
        if position.budget_assignment_allowed and (
                position.with_context(
                    budget_id=budget.id).balance_amount < 0.0):
            raise ValidationError(
                _("You can not make this modification as '%s' will have a "
                    "negative balance") % (position.name))

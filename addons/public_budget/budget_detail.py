# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class budget_detail(models.Model):
    """"""

    _name = 'public_budget.budget_detail'
    _description = 'budget_detail'

    _order = "budget_position_id"

    initial_amount = fields.Float(
        string='Initial Amount',
        required=True
        )
    # TODO borrar estos campos y metodos si no los usamos
    # amount = fields.Float(
    #     string='Amount',
    #     compute='_get_amount'
    #     )
    # draft_amount = fields.Float(
    #     string='Draft Amount',
    #     compute='_get_amounts'
    #     )
    # preventive_amount = fields.Float(
    #     string='Preventive Amount',
    #     compute='_get_amounts'
    #     )
    # definitive_amount = fields.Float(
    #     string='Definitive Amount',
    #     compute='_get_amounts'
    #     )
    # to_pay_amount = fields.Float(
    #     string='To Pay Amount',
    #     compute='_get_amounts'
    #     )
    # paid_amount = fields.Float(
    #     string='Paid Amount',
    #     compute='_get_amounts'
    #     )
    # balance_amount = fields.Float(
    #     string='Balance Amount',
    #     compute='_get_amounts'
    #     )
    state = fields.Selection(
        string='State',
        related='budget_id.state'
        )
    budget_id = fields.Many2one(
        'public_budget.budget',
        ondelete='cascade',
        string='budget_id',
        required=True
        )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        required=True,
        context={'default_type': 'normal', 'default_budget_assignment_allowed': 1},
        domain=[('budget_assignment_allowed', '=', True)]
        )

    _constraints = [
    ]

    _sql_constraints = [
        ('position_unique', 'unique(budget_position_id, budget_id)',
            _('Budget Position must be unique per Budget.'))]

    # @api.one
    # @api.depends(
    #     'amount',
    #     'budget_id.budget_modification_ids',
    #     'budget_id.budget_modification_ids.budget_modification_detail_ids',
    #     'budget_id.budget_modification_ids.budget_modification_detail_ids.budget_position_id',
    #     'budget_id.budget_modification_ids.budget_modification_detail_ids.amount',
    # )
    # def _get_amount(self):
    #     """Update available amount for each line where:
    #     -amount = amount + modifications
    #     """
    #     modification_lines = self.env['public_budget.budget_modification_detail'].search([
    #         ('budget_modification_id.budget_id', '=', self.budget_id.id),
    #         ('budget_position_id', '=', self.budget_position_id.id)])
    #     modification_amounts = [line.amount for line in modification_lines]
    #     self.amount = self.initial_amount + sum(modification_amounts)

    # @api.one
    # def _get_amounts(self):
    #     """Update the following fields with the related values to the budget
    #     and the budget position:
    #     -draft_amount: amount sum on preventive lines in draft state
    #     -preventive_amount: amount sum on preventive lines not in draft/cancel
    #     -definitive_amount: amount sum of definitive lines
    #     -to_pay_amount: amount sum of lines that has a related voucher in draft
    #     state
    #     -paid_amount: amount sum of lines that has a related voucher in open
    #     state
    #     -balance_amount: diffference between budget position and preventive
    #     amount
    #     """
    #     preventive_lines = self.env['public_budget.preventive_line'].search([
    #         ('budget_id', '=', self.budget_id.id),
    #         ('budget_position_id', '=', self.budget_position_id.id)])
    #     draft_amounts = [
    #         line.preventive_amount
    #         for line
    #         in preventive_lines
    #         if line.state == 'draft']
    #     active_preventive_lines = [
    #         line
    #         for line
    #         in preventive_lines
    #         if line.state not in ['draft', 'cancel']]
    #     preventive_amount = sum(
    #         [line.preventive_amount for line in active_preventive_lines])
    #     self.draft_amount = sum(draft_amounts)
    #     self.preventive_amount = preventive_amount
    #     self.definitive_amount = sum(
    #         [line.definitive_amount for line in active_preventive_lines])
    #     self.to_pay_amount = sum(
    #         [line.to_pay_amount for line in active_preventive_lines])
    #     self.paid_amount = sum(
    #         [line.paid_amount for line in active_preventive_lines])
    #     self.balance_amount = self.amount - preventive_amount

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

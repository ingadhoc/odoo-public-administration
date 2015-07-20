# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class budget_modification_detail(models.Model):
    """Budget Modification Detail"""

    _name = 'public_budget.budget_modification_detail'
    _description = 'Budget Modification Detail'

    amount = fields.Float(
        string='Amount',
        required=True,
        digits=dp.get_precision('Account'),
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
        context={
            'default_type': 'normal', 'default_budget_assignment_allowed': 1},
        domain=[('budget_assignment_allowed', '=', True)]
        )

    @api.one
    @api.constrains('budget_position_id', 'amount')
    def _check_modification(self):
        budget_id = self.budget_modification_id.budget_id.id
        if self.budget_position_id.budget_assignment_allowed and (
                self.with_context(
                budget_id=budget_id).budget_position_id.balance_amount < 0.0):
            raise Warning(
                _("You can not make this modification as '%s' will have a \
                    negative balance") % (self.budget_position_id.name))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

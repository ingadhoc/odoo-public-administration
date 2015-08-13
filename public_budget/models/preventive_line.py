# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class preventive_line(models.Model):
    """Preventive Line"""

    _name = 'public_budget.preventive_line'
    _description = 'Preventive Line'
    _rec_name = 'budget_position_id'

    account_id = fields.Many2one(
        'account.account',
        string='Account',
        states={'invoiced': [('readonly', True)]},
        domain=[
            ('type', 'in', ['other']),
            ('user_type.report_type', 'in', ['expense', 'asset'])]
        )
    expedient_id = fields.Many2one(
        related='transaction_id.expedient_id',
        )
    preventive_amount = fields.Float(
        string='Preventive',
        required=True,
        digits=dp.get_precision('Account'),
        states={'closed': [('readonly', True)]}
        )
    advance_line = fields.Boolean(
        string='advance_line',
        )
    remaining_amount = fields.Float(
        string='Remaining Amount',
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        )
    definitive_amount = fields.Float(
        string='Definitive Amount',
        compute='_get_amounts',
        # store=True,
        digits=dp.get_precision('Account'),
        )
    invoiced_amount = fields.Float(
        string='Invoiced Amount',
        compute='_get_amounts',
        # store=True,
        digits=dp.get_precision('Account'),
        )
    to_pay_amount = fields.Float(
        string='To Pay Amount',
        compute='_get_amounts',
        # store=True,
        digits=dp.get_precision('Account'),
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        compute='_get_amounts',
        # store=True,
        digits=dp.get_precision('Account'),
        )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('definitive', 'definitive'),
            ('invoiced', 'invoiced'),
            ('closed', 'closed'),
            ('cancel', 'Cancel')],
        string='States',
        compute='_get_state'
        )
    affects_budget = fields.Boolean(
        'Affects Budget?',
        store=True,
        compute='_get_affects_budget',
        )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        ondelete='cascade',
        string='Transaction',
        required=True
        )
    definitive_line_ids = fields.One2many(
        'public_budget.definitive_line',
        'preventive_line_id',
        string='Definitive Lines'
        )
    budget_id = fields.Many2one(
        readonly=True,
        store=True,
        related='transaction_id.budget_id'
        )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        required=True,
        states={'invoiced': [('readonly', True)]},
        context={'default_type': 'normal'},
        domain=[('type', '=', 'normal')]
        )

    @api.one
    @api.depends(
        'preventive_amount',
        'definitive_line_ids',
    )
    def _get_state(self):
        """Por ahora solo implementamos los estados invoiced y draft
        """
        state = 'draft'
        if self.invoiced_amount:
            state = 'invoiced'
        self.state = state

    @api.one
    @api.depends(
        'transaction_id.state',
        'transaction_id.type_id.with_advance_payment',
        'advance_line',
    )
    def _get_affects_budget(self):
        """Marcamos las lineas preventivas que deben ser tenidas en cuenta en
        el budget de acuerdo a el estado de la transaccion y a sí son lineas
        de adelanto o no.
        """
        affects_budget = False
        with_advance_payment = self.transaction_id.type_id.with_advance_payment
        transaction_state = self.transaction_id.state
        if with_advance_payment:
            if self.advance_line and transaction_state == 'open':
                affects_budget = True
            elif not self.advance_line and transaction_state == 'closed':
                affects_budget = True
        else:
            if not self.advance_line and transaction_state in (
                    'open', 'closed'):
                affects_budget = True
        self.affects_budget = affects_budget

    @api.one
    @api.depends(
        'advance_line',
        'preventive_amount',
        'transaction_id.advance_voucher_ids.state',
        'transaction_id.advance_voucher_ids.to_pay_amount',
        'transaction_id.advance_voucher_ids.amount',
        'definitive_line_ids.amount',
        'definitive_line_ids.invoiced_amount',
        'definitive_line_ids.to_pay_amount',
        'definitive_line_ids.paid_amount',
    )
    def _get_amounts(self):
        """Update the following fields with the related values to the budget
        and the budget position:
        -definitive_amount: amount sum of definitive lines
        -invoiced_amount: amount sum of lines that are related to an invoice
        line
        -to_pay_amount: amount sum of lines that has a related voucher in draft
        state
        -paid_amount: amount sum of lines that has a related voucher in open
        state
        -balance_amount: diffference between budget position and preventive
        amount
        """
        if self.advance_line:
            definitive_amount = to_pay_amount = sum(
                self.transaction_id.advance_voucher_ids.filtered(
                    lambda r: r.state not in ('cancel', 'draft')).mapped(
                    'to_pay_amount'))
            paid_amount = sum(
                self.transaction_id.advance_voucher_ids.filtered(
                    lambda r: r.state == 'posted').mapped(
                    'amount'))
            invoiced_amount = 0.0
        else:
            definitive_amount = sum(self.mapped(
                'definitive_line_ids.amount'))
            invoiced_amount = sum(self.mapped(
                'definitive_line_ids.invoiced_amount'))
            to_pay_amount = sum(self.mapped(
                'definitive_line_ids.to_pay_amount'))
            paid_amount = sum(self.mapped(
                'definitive_line_ids.paid_amount'))
        self.remaining_amount = self.preventive_amount - definitive_amount
        self.definitive_amount = definitive_amount
        self.invoiced_amount = invoiced_amount
        self.to_pay_amount = to_pay_amount
        self.paid_amount = paid_amount

    @api.one
    @api.constrains('definitive_line_ids', 'preventive_amount')
    def _check_number(self):
        if self.preventive_amount < self.definitive_amount:
            raise Warning(
                _("Definitive Amount can't be greater than Preventive Amount"))

    @api.one
    @api.constrains(
        'transaction_id',
        'budget_position_id',
        'preventive_amount')
    def _check_position_balance_amount(self):
        self = self.with_context(
            budget_id=self.transaction_id.budget_id.id,
            excluded_line_id=self.id,
            )
        assignment_position = self.budget_position_id.assignment_position_id
        position_balance = (assignment_position.balance_amount)
        preventive_amount = self.preventive_amount
        if position_balance < preventive_amount:
            raise Warning(_(
                "There is not enough Balance Amount to assign (%s) to Budget "
                "Position '%s'.\n"
                "* Balance available for '%s': %s") % (
                preventive_amount, self.budget_position_id.name,
                assignment_position.name, position_balance))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

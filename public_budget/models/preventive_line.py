# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


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
        string=_('Remaining Amount'),
        compute='_get_amounts',
        digits=dp.get_precision('Account'),
        store=True,
        )
    definitive_amount = fields.Float(
        string=_('Definitive Amount'),
        compute='_get_amounts',
        store=True,
        digits=dp.get_precision('Account'),
        )
    invoiced_amount = fields.Float(
        string=_('Invoiced Amount'),
        compute='_get_amounts',
        store=True,
        digits=dp.get_precision('Account'),
        )
    to_pay_amount = fields.Float(
        string=_('To Pay Amount'),
        compute='_get_amounts',
        store=True,
        digits=dp.get_precision('Account'),
        )
    paid_amount = fields.Float(
        string=_('Paid Amount'),
        compute='_get_amounts',
        store=True,
        digits=dp.get_precision('Account'),
        )
    state = fields.Selection(
        selection=[
            ('draft', _('Draft')),
            ('open', _('Open')),
            ('definitive', _('Definitive')),
            ('invoiced', _('Invoiced')),
            ('closed', _('Closed')),
            ('cancel', _('Cancel'))],
        string=_('States'),
        compute='_get_state',
        store=True,
        )
    affects_budget = fields.Boolean(
        _('Affects Budget?'),
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
        'invoiced_amount',
    )
    def _get_state(self):
        """Por ahora solo implementamos los estados invoiced y draft
        """
        _logger.info('Getting state for preventive line %s' % self.id)
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
        # este depende de una funcion
        'transaction_id.advance_preventive_amount',
        # este depende de otras
        'transaction_id.advance_to_pay_amount',
        'transaction_id.advance_paid_amount',
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
        _logger.info('Getting amounts for preventive line %s' % self.id)
        # TODO this should be improoved and dependency to advance_voucher_ids
        # or to advance amounst must be removed
        if self.advance_line:
            _logger.info('Getting advance line values')
            transaction = self.transaction_id
            advance_preventive_amount = transaction.advance_preventive_amount
            if advance_preventive_amount:
                preventive_perc = (
                    self.preventive_amount /
                    advance_preventive_amount)
            else:
                preventive_perc = 0.0
            definitive_amount = to_pay_amount = (
                transaction.advance_to_pay_amount * preventive_perc)
            paid_amount = (transaction.advance_paid_amount * preventive_perc)
            invoiced_amount = 0.0
        else:
            _logger.info('Getting none advance line values')
            definitive_lines = self.definitive_line_ids
            if not definitive_lines:
                return False

            # Add this to allow analysis between dates
            # from_date = self._context.get('analysis_from_date', False)
            to_date = self._context.get('analysis_to_date', False)

            filter_domain = []
            # if from_date:
            #     filter_domain += [('issue_date', '>=', from_date)]
            if to_date:
                filter_domain += [('issue_date', '<=', to_date)]
            if filter_domain:
                filter_domain += [('id', 'in', definitive_lines.ids)]
                definitive_lines = definitive_lines.search(filter_domain)

            definitive_amount = sum(definitive_lines.mapped('amount'))
            invoiced_amount = sum(definitive_lines.mapped('invoiced_amount'))
            to_pay_amount = sum(definitive_lines.mapped('to_pay_amount'))
            paid_amount = sum(definitive_lines.mapped('paid_amount'))
        self.remaining_amount = self.preventive_amount - definitive_amount
        self.definitive_amount = definitive_amount
        self.invoiced_amount = invoiced_amount
        self.to_pay_amount = to_pay_amount
        self.paid_amount = paid_amount
        _logger.info('Finish getting amounts for preventive line %s' % self.id)

    @api.one
    @api.constrains('account_id', 'transaction_id')
    def check_type_company(self):
        if (
                self.account_id and self.transaction_id and
                self.account_id.company_id != self.transaction_id.company_id
                ):
            raise Warning(_(
                'Transaction Company and Account Company must be the same!'))

    @api.one
    @api.constrains('definitive_line_ids', 'preventive_amount')
    def _check_number(self):
        if self.transaction_id.company_id.currency_id.round(
                self.preventive_amount - self.definitive_amount) < 0.0:
            raise Warning(
                _("Definitive Amount can't be greater than Preventive Amount"))

    @api.one
    @api.constrains(
        'preventive_amount')
    def check_budget_state_open(self):
        if self.budget_id and self.budget_id.state not in 'open':
            raise Warning(
                'Solo puede cambiar afectaciones preventivas si '
                'el presupuesto está abierto')

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
        if not assignment_position:
            raise Warning(_(
                "The selected budget position (%s) has not a related assigment"
                " position!" % self.budget_position_id.name))
        position_balance = (assignment_position.balance_amount)
        preventive_amount = self.preventive_amount
        if position_balance < preventive_amount:
            raise Warning(_(
                "There is not enough Balance Amount to assign (%s) to Budget "
                "Position '%s'.\n"
                "* Balance available for '%s': %s") % (
                preventive_amount, self.budget_position_id.name,
                assignment_position.name, position_balance))

    @api.one
    def unlink(self):
        if self.definitive_line_ids:
            raise Warning(_(
                "You can not delete a preventive line that has definitive "
                "lines"))
        return super(preventive_line, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

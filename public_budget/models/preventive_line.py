# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class PreventiveLine(models.Model):

    _name = 'public_budget.preventive_line'
    _description = 'Preventive Line'
    _rec_name = 'budget_position_id'

    account_id = fields.Many2one(
        'account.account',
        string='Account',
        states={'invoiced': [('readonly', True)]},
        domain="["
        "('internal_type', '=', 'other'), "
        "('company_id', '=', company_id), "
        "('deprecated', '=', False)]",
    )
    company_id = fields.Many2one(
        related='transaction_id.company_id',
        readonly=True,
    )
    currency_id = fields.Many2one(
        related='transaction_id.currency_id',
        readonly=True,
    )
    expedient_id = fields.Many2one(
        related='transaction_id.expedient_id',
        readonly=True,
    )
    preventive_amount = fields.Monetary(
        string='Preventive',
        required=True,
        states={'closed': [('readonly', True)]}
    )
    advance_line = fields.Boolean(
        string='Advance Line?',
    )
    remaining_amount = fields.Monetary(
        compute='_get_amounts',
        store=True,
    )
    definitive_amount = fields.Monetary(
        compute='_get_amounts',
        store=True,
    )
    invoiced_amount = fields.Monetary(
        compute='_get_amounts',
        store=True,
    )
    to_pay_amount = fields.Monetary(
        compute='_get_amounts',
        store=True,
    )
    paid_amount = fields.Monetary(
        compute='_get_amounts',
        store=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', _('Draft')),
            ('open', _('Open')),
            ('definitive', _('Definitive')),
            ('invoiced', _('Invoiced')),
            ('closed', _('Closed')),
            ('cancel', _('Cancel'))],
        compute='_get_state',
        store=True,
    )
    affects_budget = fields.Boolean(
        'Affects Budget?',
        store=True,
        compute='_get_affects_budget',
    )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transaction',
        required=True,
        auto_join=True,
    )
    definitive_line_ids = fields.One2many(
        'public_budget.definitive_line',
        'preventive_line_id',
        string='Definitive Lines',
        auto_join=True,
    )
    budget_id = fields.Many2one(
        readonly=True,
        store=True,
        related='transaction_id.budget_id',
        auto_join=True,
    )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        required=True,
        states={'invoiced': [('readonly', True)]},
        context={'default_type': 'normal'},
        domain=[('type', '=', 'normal')],
        auto_join=True,
    )
    definitive_partner_type = fields.Selection(
        related='transaction_id.type_id.definitive_partner_type'
    )

    @api.onchange('budget_position_id')
    def change_budget_position(self):
        self.account_id = self.budget_position_id.default_account_id

    @api.multi
    @api.depends(
        'invoiced_amount',
    )
    def _get_state(self):
        """Por ahora solo implementamos los estados invoiced y draft
        """
        for rec in self:
            _logger.info('Getting state for preventive line %s' % rec.id)
            state = 'draft'
            if rec.invoiced_amount:
                state = 'invoiced'
            rec.state = state

    @api.multi
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
        for rec in self:
            affects_budget = False
            with_advance_payment = (
                rec.transaction_id.type_id.with_advance_payment)
            transaction_state = rec.transaction_id.state
            if with_advance_payment:
                if rec.advance_line and transaction_state == 'open':
                    affects_budget = True
                elif not rec.advance_line and transaction_state == 'closed':
                    affects_budget = True
            else:
                if not rec.advance_line and transaction_state in (
                        'open', 'closed'):
                    affects_budget = True
            rec.affects_budget = affects_budget

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
        -to_pay_amount: amount sum of lines that has a related payment in draft
        state
        -paid_amount: amount sum of lines that has a related payment in open
        state
        -balance_amount: diffference between budget position and preventive
        amount
        """
        _logger.info('Getting amounts for preventive line %s' % self.id)
        # TODO this should be improoved and dependency to payment_groups_ids
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

            invoiced_amount_field = 'invoiced_amount'
            to_pay_amount_field = 'to_pay_amount'
            paid_amount_field = 'paid_amount'

            # Add this to allow analysis between dates, we used computed fields
            # in this case instead of normal fields
            to_date = self._context.get('analysis_to_date', False)
            if to_date:
                filter_domain = [
                    ('issue_date', '<=', to_date),
                    ('id', 'in', definitive_lines.ids)]
                definitive_lines = definitive_lines.search(filter_domain)
                invoiced_amount_field = 'computed_invoiced_amount'
                to_pay_amount_field = 'computed_to_pay_amount'
                paid_amount_field = 'computed_paid_amount'
            definitive_amount = invoiced_amount = \
                to_pay_amount = paid_amount = 0
            for dl in definitive_lines:
                definitive_amount += dl.amount
                invoiced_amount += getattr(dl, invoiced_amount_field)
                to_pay_amount += getattr(dl, to_pay_amount_field)
                paid_amount += getattr(dl, paid_amount_field)
        self.remaining_amount = self.preventive_amount - definitive_amount
        self.definitive_amount = definitive_amount
        self.invoiced_amount = invoiced_amount
        self.to_pay_amount = to_pay_amount
        self.paid_amount = paid_amount
        _logger.info('Finish getting amounts for preventive line %s' % self.id)

    @api.multi
    @api.constrains('account_id', 'transaction_id')
    def check_type_company(self):
        for rec in self:
            if (
                    rec.account_id and rec.transaction_id and
                    rec.account_id.company_id != rec.transaction_id.company_id
            ):
                raise ValidationError(_(
                    'Transaction Company and Account Company must be the '
                    'same!'))

    @api.multi
    @api.constrains('definitive_line_ids', 'preventive_amount')
    def _check_number(self):
        for rec in self:
            if rec.currency_id.round(
                    rec.preventive_amount - rec.definitive_amount) < 0.0:
                raise ValidationError(_(
                    "Definitive Amount can't be greater than Preventive "
                    "Amount"))

    @api.multi
    @api.constrains(
        'preventive_amount')
    def check_budget_state_open(self):
        for rec in self:
            if rec.budget_id and rec.budget_id.state not in 'open':
                raise ValidationError(
                    'Solo puede cambiar afectaciones preventivas si '
                    'el presupuesto está abierto')

    @api.multi
    @api.constrains(
        'transaction_id',
        # no agregamos affects_budget sobre este campo ya que algunas veces,
        # de manera aleatoria, termina dando un error que tal vez tenga que
        # ver en el ordne en que se computan las cosas.
        # verificamos esto desde una constraint sobre state de las
        # transacciones. El error era:
        # unsupported operand type(s) for +=: 'float' and 'NoneType'
        # 'affects_budget',
        'budget_position_id',
        'preventive_amount')
    def _check_position_balance_amount(self):
        # filtamos por affects_budget porque cuando estamos cargando las
        # definitivas de una transacción de adelanto, como hasta que se cierre
        # todo se suman las de adelanto, no queremos que se calcule para las
        # definitivas
        for rec in self.filtered('affects_budget'):
            rec = rec.with_context(
                budget_id=rec.transaction_id.budget_id.id,
                excluded_line_id=rec.id,
            )
            assignment_position = rec.budget_position_id.assignment_position_id
            if not assignment_position:
                raise ValidationError(_(
                    "The selected budget position (%s) has not a related "
                    "assigment position!" % rec.budget_position_id.name))
            position_balance = (assignment_position.balance_amount)
            preventive_amount = rec.preventive_amount
            if position_balance < preventive_amount:
                raise ValidationError(_(
                    "There is not enough Balance Amount to assign (%s) to "
                    "Budget Position '%s' (%s).\n"
                    "* Balance available for '%s' (%s): %s") % (
                    preventive_amount, rec.budget_position_id.name,
                    rec.budget_position_id.code,
                    assignment_position.name,
                    assignment_position.code, position_balance))

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.definitive_line_ids:
                raise ValidationError(_(
                    "You can not delete a preventive line that has definitive "
                    "lines"))
        return super(PreventiveLine, self).unlink()

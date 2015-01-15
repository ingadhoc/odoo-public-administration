# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class preventive_line(models.Model):
    """Preventive Line"""

    _name = 'public_budget.preventive_line'
    _description = 'Preventive Line'

    name = fields.Char(
        string='Name',
        required=True,
        states={'invoiced': [('readonly', True)], 'closed': [('readonly', True)], 'cancel': [('readonly', True)]}
        )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        states={'invoiced': [('readonly', True)], 'closed': [('readonly', True)]},
        domain=[('type', 'in', ['other']), ('user_type.report_type', 'in', ['expense','asset'])]
        )
    preventive_amount = fields.Float(
        string='Preventive',
        required=True,
        states={'closed': [('readonly', True)]}
        )
    preventive_status = fields.Selection(
        [(u'draft', u'Draft'), (u'confirmed', u'Confirmed')],
        string='Status',
        readonly=True,
        required=True,
        states={'open': [('readonly', False)], 'confirmed': [('readonly', False)]},
        default='draft'
        )
    available_account_ids = fields.Many2one(
        'account.account',
        string='available_account_ids'
        )
    advance_line = fields.Boolean(
        string='advance_line'
        )
    payment_line_id = fields.Many2one(
        comodel_name='payment.line',
        string='Payment line',
        readonly=True
        )
    remaining_amount = fields.Float(
        string='Remaining Amount',
        compute='_get_amounts'
        )
    definitive_amount = fields.Float(
        string='Definitive Amount',
        compute='_get_amounts'
        )
    invoiced_amount = fields.Float(
        string='Invoiced Amount',
        compute='_get_amounts'
        )
    to_pay_amount = fields.Float(
        string='To Pay Amount',
        compute='_get_amounts'
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        compute='_get_amounts'
        )
    available_account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Available Accounts',
        readonly=True,
        related='budget_position_id.available_account_ids'
        )
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('open', 'Open'), ('confirmed', 'confirmed'), ('definitive', 'definitive'), ('invoiced', 'invoiced'), ('closed', 'closed'), ('cancel', 'Cancel'), ('inactive', 'Inactive')],
        string='States',
        compute='_get_state'
        )
    accounting_state = fields.Selection(
        selection=[('draft', 'Draft'), ('confirmed', 'Confirmed')],
        string='Accounting State',
        store=True,
        compute='_get_accounting_state'
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
        string='Definitive Lines',
        readonly=True,
        states={'confirmed': [('readonly', False)], 'definitive': [('readonly', False)], 'invoiced': [('readonly', False)]}
        )
    budget_id = fields.Many2one(
        'public_budget.budget',
        string='Budget',
        required=True,
        states={'invoiced': [('readonly', True)], 'closed': [('readonly', True)], 'cancel': [('readonly', True)]},
        domain=[('state', 'not in', ['closed', 'pre_closed'])]
        )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        required=True,
        states={'invoiced': [('readonly', True)], 'closed': [('readonly', True)], 'cancel': [('readonly', True)]},
        context={'default_type': 'normal'},
        domain=[('type', '=', 'normal')]
        )

    _constraints = [
    ]

    @api.one
    @api.depends(
        'preventive_amount',
        'definitive_line_ids',
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

        definitive_amount = False
        invoiced_amount = False
        to_pay_amount = False
        paid_amount = False
        if self.advance_line:
            if self.payment_line_id.order_id.state == 'done':
                definitive_amount = self.preventive_amount
                to_pay_amount = self.preventive_amount
                if self.payment_line_id.voucher_id.state == 'posted':
                    paid_amount = self.preventive_amount
        else:
            definitive_amount = sum([
                definitive.amount
                for definitive in self.definitive_line_ids])
            invoiced_amount = sum([
                definitive.invoiced_amount
                for definitive in self.definitive_line_ids])
            to_pay_amount = sum([
                definitive.to_pay_amount
                for definitive in self.definitive_line_ids])
            paid_amount = sum([
                definitive.paid_amount for definitive in self.definitive_line_ids])

        self.remaining_amount = self.preventive_amount - definitive_amount
        self.definitive_amount = definitive_amount
        self.invoiced_amount = invoiced_amount
        self.to_pay_amount = to_pay_amount
        self.paid_amount = paid_amount

    @api.one
    @api.depends(
        'transaction_id',
        'preventive_status',
        'definitive_line_ids',
        'budget_id',
        'budget_id.state',
    )
    def _get_state(self):
        """ Usamos "state" para definir cuando son modificables algunos
        campos:
        * draft: cuando esta marcada como "borrador" o el proyecto en borrador
            Se puede modificar
        * confirmed: cuando esta marcada como confirm
            Se pueden agregar definitivas
        * definitive: cuando existe una definitiva
            No se puede modificar el preventive_status de la preventiva
        * invoiced: si existe una factura para al menos una definitiva
            Ya no se puede moficiar nada, solo se puede modificar el importe
            (que sera restricto a la suma de los importes definitivos) y
            las lineas definitivas. A su vez, cada linea definitiva tiene la
            restriccion de poder ser modificada solo si no fue facturada.
        * closed: si el budget es "pre-closed o closed" o transaccion closed
            No se puede modificar nada
        * cancel: si el budget esta en "cancel" o transaccion cancel
            No se puede modificar nada
        """
        # transacion states closed, cancel, draft, open
        state = self.transaction_id.state
        if self.budget_id:
            # states draft, cancel, closed or open
            state = self.budget_id.state
            if self.budget_id.state == 'open':
                if self.preventive_status == 'confirmed':
                    state = 'confirmed'
                if self.definitive_line_ids:
                    state = 'definitive'
                    def_state = [x.state for x in self.definitive_line_ids]
                    if 'invoiced' in def_state:
                        state = 'invoiced'
        self.state = state

    @api.one
    @api.depends(
        'transaction_id',
        'transaction_id.state',
        'transaction_id.type_id.with_advance_payment',
        'budget_id',
        'budget_id.state',
        'advance_line',
        'preventive_status',
    )
    def _get_accounting_state(self):
        """
        Usamos "accounting_state" para saber si se deben tener en cuenta en el
        calculo de las budgets positions:
        * draft: cuando esta marcada como "borrador" o el proyecto en borrador
            Se tiene en cuenta como draft
        * preventive: cuando es

        If accounting state == false, then it doesn't mean anything.
        """
        accounting_state = False
        if self.transaction_id.state != 'cancel':
            # Presupuestos no cancelados
            if self.budget_id.state != 'cancel':
                # Para transacciones con adelanto
                if self.transaction_id.type_id.with_advance_payment:
                    # Si es linea de adelanto, se tiene en cuenta en draft y
                    # open
                    if self.advance_line and self.transaction_id.state in (
                            'draft', 'open'):
                        accounting_state = 'confirmed'
                        # accounting_state = self.preventive_status
                    # Si no es linea de adelanto, se tiene en cuenta en closed
                    if not self.advance_line and self.transaction_id.state in (
                            'closed'):
                        accounting_state = 'confirmed'
                        # accounting_state = self.preventive_status
                else:
                    if self.budget_id.state == 'draft':
                        accounting_state = 'draft'
                    else:
                        accounting_state = self.preventive_status
        self.accounting_state = accounting_state

    @api.one
    @api.constrains(
        'budget_id',
        'budget_position_id',
        'preventive_amount')
    def _check_position_balance_amount(self):
        self = self.with_context(budget_id=self.budget_id.id)
        if self.budget_position_id.budget_assignment_allowed and self.budget_position_id.balance_amount < 0.0:
            raise Warning(
                _("There is not Enought Balance Amount on this Budget Position '%s'") %
                (self.budget_position_id.name))

    @api.one
    @api.constrains('definitive_line_ids', 'preventive_amount')
    def _check_number(self):
        if self.preventive_amount < self.definitive_amount:
            raise Warning(
                _("Definitive Amount can't be greater than Preventive Amount"))

    @api.one
    def unlink(self):
        if self.preventive_status == 'confirmed':
            raise Warning(_(
                "You can not delete a confirmed preventive line"))
        return super(preventive_line, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class AccountPaymentGroup(models.Model):
    """"""

    _inherit = 'account.payment.group'

    # TODO ver como agregar esto mas lindo
    # We add signature states
    # state = fields.Selection(
    #     selection=[
    #         ('draft', _('Boorador')),
    #         ('confirmed', _('Confirmado')),
    #         ('signature_process', _('En Proceso de Firma')),
    #         ('signed', _('Firmado')),
    #         ('cancel', _('Cancelado')),
    #         ('proforma', _('Pro-forma')),
    #         # we also change posted for paid
    #         ('posted', _('Pagado'))
    #     ])
    budget_id = fields.Many2one(
        related='transaction_id.budget_id',
        readonly=True,
        store=True,
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expedient',
        readonly=True,
        # required=True,
        # domain=[('type', '=', 'payment'), ('state', '=', 'open')],
        domain="[('type', '=', 'payment'), ('state', '=', 'open'), "
        "('current_location_id', 'in', user_location_ids[0][2]), "
        "('in_transit', '=', False)]",
        context={'default_type': 'payment'},
        states={'draft': [('readonly', False)]}
    )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transaction',
        # required=True,
        readonly=True,
    )
    budget_position_ids = fields.Many2many(
        relation='voucher_position_rel',
        comodel_name='public_budget.budget_position',
        string='Partidas Presupuestarias Relacionadas',
        compute='_get_budget_positions_and_invoices',
        search='_search_budget_positions',
    )
    invoice_ids = fields.Many2many(
        comodel_name='account.invoice',
        string='Facturas Relacionadas',
        compute='_get_budget_positions_and_invoices'
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string=_('Partners'),
        compute='_get_partners'
    )
    partner_id = fields.Many2one(
        domain="[('id', 'in', partner_ids[0][2])]",
    )
    # advance_request_line_ids = fields.One2many(
    #     'public_budget.advance_request_line',
    #     'voucher_id',
    #     'Advance Request Line',
    #     )
    advance_request_id = fields.Many2one(
        'public_budget.advance_request',
        'Advance Request',
        readonly=True,
    )
    transaction_with_advance_payment = fields.Boolean(
        readonly=True,
        store=True,
        related='transaction_id.type_id.with_advance_payment',
    )
    user_location_ids = fields.Many2many(
        compute='get_user_locations',
        comodel_name='public_budget.location',
        string='User Locations',
    )
    payment_base_date = fields.Date(
        string='Payment Base Date',
        readonly=True,
        default=fields.Date.context_today,
        states={'draft': [('readonly', False)]},
        help='Date used to calculate payment date',
    )
    payment_days = fields.Integer(
        string='Payment Days',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Days added to payment base date to get the payment date',
    )
    payment_date = fields.Date(
        compute='get_payment_date',
        string='Fecha de Pago',
        states={},
        store=True,
    )
    # TODO ver si necesitamos activar todos estos campos
    # net_amount = fields.Monetary(
    #     states={'confirmed': [('readonly', False)]}
    # )
    # issued_check_ids = fields.One2many(
    #     states={'confirmed': [('readonly', False)]}
    # )
    # withholding_ids = fields.One2many(
    #     states={'confirmed': [('readonly', False)]}
    # )
    # paid_withholding_ids = fields.Many2many(
    #     comodel_name='account.voucher.withholding',
    #     string='Retenciones Pagadas',
    #     help='Retenciones pagadas con este voucher',
    #     compute='_get_paid_withholding'
    # )
    show_print_receipt_button = fields.Boolean(
        _('Show Print Receipt Button'),
        compute='get_show_print_receipt_button',
    )

    @api.one
    @api.constrains('receiptbook_id', 'state', 'type')
    def check_receiptbook(self):
        """
        """
        if (
                self.state == 'confirmed' and
                self.type == 'payment' and
                not self.receiptbook_id
        ):
            raise ValidationError(_(
                'You can not confirm a payment order without ReceiptBook'))

    @api.one
    @api.constrains('receiptbook_id', 'state')
    def add_force_number(self):
        """
        we use force number as a hack to compute document number on creation
        or any write
        """
        # voucher_type = vals.get(
        #     'type', self._context.get('default_type', False))
        # receiptbook = self.receiptbook_id.browse(
        #     vals.get('receiptbook_id', False))
        if (
                self.receiptbook_id and
                self.type == 'payment' and
                not self.force_number and
                not self.document_number
        ):
            self.force_number = self.env['ir.sequence'].next_by_id(
                self.receiptbook_id.sequence_id.id)
            # vals['force_number'] = force_number
        # return super(account_voucher, self).create(vals)

    @api.multi
    def _get_receiptbook(self):
        self.ensure_one()
        # we dont want any receiptbook as default
        return False

    @api.one
    @api.depends('issued_check_ids.state', 'state')
    def get_show_print_receipt_button(self):
        show_print_receipt_button = False

        # not_handed_checks = self.issued_check_ids.filtered(
        #     lambda r: r.state not in (
        #         'handed', 'returned', 'debited', 'changed'))
        # parece mas facil chequear por los que tengo en mano
        # total los cancelados y en borrador se controlan por estado del
        # voucher
        not_handed_checks = self.issued_check_ids.filtered(
            lambda r: r.state in (
                'holding', 'to_be_handed'))

        if self.state == 'posted' and not not_handed_checks:
            show_print_receipt_button = True
        self.show_print_receipt_button = show_print_receipt_button
        # dejamos esta parte de codigo por si en tmc piden que si se pueda
        # imprimir sin importar si fue entregado o no
        # if self.state == 'posted':
        #     show_print_receipt_button = True
        # self.show_print_receipt_button = show_print_receipt_button

    @api.one
    @api.depends('payment_base_date', 'payment_days')
    def get_payment_date(self):
        current_date = False
        business_days_to_add = self.payment_days
        if self.payment_base_date:
            current_date = fields.Date.from_string(self.payment_base_date)
            while business_days_to_add > 0:
                current_date = current_date + relativedelta(days=1)
                weekday = current_date.weekday()
                # sunday = 6
                if weekday >= 5 or self.env[
                        'hr.holidays.public'].is_public_holiday(current_date):
                    continue
                # if current_date in holidays:
                #     continue
                business_days_to_add -= 1
        self.payment_date = fields.Date.to_string(current_date)

    @api.constrains('state', 'journal_id', 'to_pay_amount')
    def check_journal_amount_restriction_with_double_validation(self):
        """
        We add this constraint that lins double validation module and
        voucher reconcile
        """
        for voucher in self.filtered(lambda x: x.state == 'confirmed'):
            journal = self.journal_id
            if (
                    journal.voucher_amount_restriction == 'cant_be_cero' and
                    not voucher.to_pay_amount
            ):
                raise ValidationError(_(
                    "On Journal '%s' to pay amount can't be cero!\n"
                    "* Voucher id: %i") % (journal.name, voucher.id))
            elif (
                    journal.voucher_amount_restriction == 'must_be_cero' and
                    voucher.to_pay_amount
            ):
                raise ValidationError(_(
                    "On Journal '%s' to pay amount must be cero!\n"
                    "* Voucher id: %i") % (journal.name, voucher.id))
        return True

    # @api.one
    # def _get_paid_withholding(self):
    #     paid_move_ids = [
    #         x.move_line_id.move_id.id for x in self.line_ids if x.amount]
    #     paid_withholdings = self.env['account.voucher.withholding'].search([(
    #         'move_line_id.tax_settlement_move_id', 'in', paid_move_ids)])
    #     self.paid_withholding_ids = paid_withholdings

    @api.one
    # dummy depends to compute values on create
    @api.depends('transaction_id')
    def get_user_locations(self):
        self.user_location_ids = self.env.user.location_ids

    @api.model
    def _search_budget_positions(self, operator, value):
        return [
            ('line_ids.move_line_id.invoice.invoice_line_ids.'
                'definitive_line_id.preventive_line_id.budget_position_id',
                operator, value)]

    @api.one
    def _get_budget_positions_and_invoices(self):
        self.invoice_ids = self.line_ids.filtered('amount').mapped(
            'move_line_id.invoice')
        self.budget_position_ids = self.invoice_ids.mapped(
            'invoice_line_ids.definitive_line_id.preventive_line_id.'
            'budget_position_id')

    @api.one
    @api.depends(
        'transaction_id',
    )
    def _get_partners(self):
        _logger.info('Get partners from transaction')
        self.partner_ids = self.env['res.partner']
        partner_ids = []
        if self.transaction_id:
            if self.transaction_id.type_id.with_advance_payment and (
                    self.transaction_id.partner_id):
                partner_ids = [
                    self.transaction_id.partner_id.commercial_partner_id.id]
            else:
                partner_ids = self.mapped(
                    'transaction_id.supplier_ids.commercial_partner_id')
        self.partner_ids = partner_ids

    @api.model
    def get_move_lines(self, ttype, partner_id, journal_id):
        """
        We add transaction to get_move_lines function
        """
        _logger.info('Get move lines filtered by transaction')
        move_lines = super(AccountPaymentGroup, self).get_move_lines(
            ttype, partner_id, journal_id)
        transaction_id = self._context.get(
            'transaction_id',
            self._context.get('transaction_id', False))
        if transaction_id:
            move_lines = move_lines.filtered(
                lambda r: (
                    # sacamos estas porquer serian por ej. las liquidaciones
                    # not r.invoice or
                    # agregamos esto para que traiga las devoluciones de
                    # adelantos, en realidad va a traer cualquier cosa
                    # que sea un credito
                    r.debit or
                    r.invoice.transaction_id.id == transaction_id))
        # agregamos esto para que no lleve facturas a vouchers que no esten
        # dentro del marco de una transaccion (por ej. pago de adelantos)
        else:
            move_lines = move_lines.filtered(lambda r: (not r.invoice))
        return move_lines

    def writeoff_move_line_get(
            self, cr, uid, voucher_id, line_total, move_id, name,
            company_currency, current_currency, context=None):
        """Cambiamos la cuenta que usa el adelanto para utilizar aquella que
        viene de la transaccion de adelanto o del request"""
        _logger.info('Replace account using for advance transaction')
        res = super(AccountPaymentGroup, self).writeoff_move_line_get(
            cr, uid, voucher_id, line_total, move_id, name,
            company_currency, current_currency, context=context)
        voucher = self.browse(cr, uid, voucher_id, context=context)

        if res:
            if voucher.transaction_with_advance_payment:
                account = voucher.transaction_id.type_id.advance_account_id
                if not account:
                    raise ValidationError(_(
                        'In payment of advance transaction type, you need to '
                        'set an advance account in transaction type!'))
                res['account_id'] = account.id
            elif voucher.advance_request_id:
                res['account_id'] = (
                    voucher.advance_request_id.type_id.account_id.id)
        return res

    @api.multi
    def check_to_sign_process(self):
        """
        """
        for voucher in self:
            if self.currency_id.round(voucher.amount - voucher.to_pay_amount):
                raise ValidationError(_(
                    'You can not send to sign process a Voucher '
                    'that has Total Amount different from To Pay Amount'))
        return True

# TODO ver donde agregamos esto sin que dependa de loc ar
# modificamos estas funciones para que si esta en borrador no setee ningun
# valor por defecto
# @api.onchange('retencion_ganancias', 'partner_id_copy')
# def change_retencion_ganancias(self):
#     def_regimen = False
#     if self.state != 'draft' and self.retencion_ganancias == 'nro_regimen':
#         cia_regs = self.company_regimenes_ganancias_ids
#         partner_regimen = self.partner_id.default_regimen_ganancias_id
#         if partner_regimen and partner_regimen in cia_regs:
#             def_regimen = partner_regimen
#         elif cia_regs:
#             def_regimen = cia_regs[0]
#     self.regimen_ganancias_id = def_regimen

# @api.onchange('company_regimenes_ganancias_ids')
# def change_company_regimenes_ganancias(self):
#     if (
#             self.state != 'draft' and
#             self.company_regimenes_ganancias_ids and
#             self.type == 'payment'):
#         self.retencion_ganancias = 'nro_regimen'

    @api.one
    @api.constrains('state')
    def update_invoice_amounts(self):
        _logger.info('Updating invoice amounts from voucher')
        # when voucher state changes we recomputed related invoice values
        # we could improove this filtering by relevant states
        self.invoice_ids.sudo()._compute_to_pay_amount()

    @api.one
    @api.constrains('confirmation_date', 'date')
    def check_date(self):
        _logger.info('Checking date')
        if not self.confirmation_date or not self.date:
            return True
        if self.date < self.confirmation_date:
            raise ValidationError(_(
                'La fecha de validacion del pago no puede ser menor a la fecha'
                ' de confirmación'))

    @api.one
    @api.constrains('state')
    def check_to_pay_amount(self):
        if self.state != 'confirmed':
            return True
        to_remove_lines = self.env['account.voucher.line'].search([
            ('voucher_id', '=', self.id),
            ('amount', '=', 0.0),
        ])
        to_remove_lines.unlink()

    @api.multi
    def proforma_voucher(self):
        if (
                self.expedient_id and self.expedient_id.current_location_id
                not in self.user_location_ids):
            raise ValidationError(
                'No puede confirmar un pago si el expediente no está en una '
                'ubicación autorizada para ústed')
        return super(AccountPaymentGroup, self).proforma_voucher()

    @api.one
    @api.constrains('confirmation_date', 'date')
    def check_confirmation_date(self):
        _logger.info('Checking confirmation date')
        if not self.confirmation_date:
            return True
        for invoice in self.invoice_ids:
            if self.confirmation_date < invoice.date_invoice:
                raise ValidationError(_(
                    'La fecha de confirmación no puede ser menor a la fecha '
                    'de la factura que se esta pagando'))

    @api.one
    @api.constrains('advance_amount', 'transaction_id', 'state')
    def check_voucher_transaction_amount(self):
        """
        """
        _logger.info('Checking transaction amount on voucher %s' % self.id)
        if self.transaction_with_advance_payment:
            # forzamos el recalculo porque al ser store no lo recalculaba
            self.transaction_id._get_advance_remaining_amount()
            advance_remaining_amount = self.currency_id.round(
                self.transaction_id.advance_remaining_amount)
            if advance_remaining_amount < 0.0:
                raise ValidationError(_(
                    'In advance transactions, payment orders amount (%s) can '
                    'not be greater than transaction advance remaining amount '
                    '(%s)') % (
                    self.advance_amount,
                    advance_remaining_amount + self.advance_amount))


class AccountPaymentGroup_line(models.Model):
    """"""

    _inherit = 'account.voucher.line'

    to_pay_amount = fields.Monetary(
        related='move_line_id.invoice.to_pay_amount',
        # TODO reactivar si es necesario o borrar
        # store=True,
        readonly=True,
    )

    @api.one
    # @api.constrains('amount_unreconciled', 'amount')
    def check_voucher_transaction_amount(self):
        """
        """
        _logger.info(
            'Checking voucher line transaction amount for voucher %s' % (
                self.id))
        if self.amount > self.amount_unreconciled:
            raise ValidationError(_(
                'In each line, Amount can not be greater than Open Balance'))

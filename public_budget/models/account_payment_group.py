# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class AccountPaymentGroup(models.Model):
    """"""

    _inherit = 'account.payment.group'

    # We add signature states
    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('confirmed', 'Confirmado'),
            ('signature_process', 'En Proceso de Firma'),
            ('signed', 'Firmado'),
            # we also change posted for paid
            ('posted', 'Pagado')
        ])
    budget_id = fields.Many2one(
        related='transaction_id.budget_id',
        readonly=True,
        store=True,
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expedient',
        readonly=True,
        domain="[('type', '=', 'payment'), ('state', '=', 'open'), "
        "('current_location_id', 'in', user_location_ids[0][2]), "
        "('in_transit', '=', False)]",
        context={'default_type': 'payment'},
        states={'draft': [('readonly', False)]}
    )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        string='Transaction',
        readonly=True,
    )
    budget_position_ids = fields.Many2many(
        relation='voucher_position_rel',
        comodel_name='public_budget.budget_position',
        string='Partidas Relacionadas',
        help='Partidas Presupuestarias Relacionadas',
        compute='_get_budget_positions_and_invoices',
        search='_search_budget_positions',
    )
    # lo agregamos por compatiblidad hacia atras y tmb porque es mas facil
    invoice_ids = fields.Many2many(
        comodel_name='account.invoice',
        string='Facturas Relacionadas',
        compute='_get_budget_positions_and_invoices'
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Partners',
        compute='_get_partners'
    )
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
    payment_min_date = fields.Date(
        compute='get_payment_min_date',
        string='Fecha Min. de Pago',
        help='El pago no puede ser validado antes de esta fecha',
        store=True,
    )
    confirmation_date = fields.Date(
        'Fecha de Confirmación',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    # hacemos que la fecha de pago no sea obligatoria ya que seteamos fecha
    # de validacion si no estaba seteada
    payment_date = fields.Date(
        required=False
    )
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

    @api.multi
    def post(self):
        for rec in self:
            if not rec.payment_date:
                rec.confirmation_date = fields.Date.today()
            if (
                    rec.expedient_id and rec.expedient_id.current_location_id
                    not in rec.user_location_ids):
                raise ValidationError(
                    'No puede validar un pago si el expediente no está en '
                    'una ubicación autorizada para ústed')
        return super(AccountPaymentGroup, self).confirm()

    @api.multi
    @api.constrains('payment_date')
    def update_payment_date(self):
        for rec in self:
            rec.payment_ids.write({'payment_date': rec.payment_date})

    @api.multi
    def confirm(self):
        for rec in self:
            if not rec.confirmation_date:
                rec.confirmation_date = fields.Date.today()
        return super(AccountPaymentGroup, self).confirm()

    @api.multi
    def _get_receiptbook(self):
        # we dont want any receiptbook as default
        return False

    @api.multi
    @api.depends('payment_ids.check_ids.state', 'state')
    def get_show_print_receipt_button(self):
        show_print_receipt_button = False

        not_handed_checks = self.payment_ids.mapped('check_ids').filtered(
            lambda r: r.state in (
                'holding', 'to_be_handed'))

        if self.state == 'posted' and not not_handed_checks:
            show_print_receipt_button = True
        self.show_print_receipt_button = show_print_receipt_button

    @api.one
    @api.depends('payment_base_date', 'payment_days')
    def get_payment_min_date(self):
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
        self.payment_min_date = fields.Date.to_string(current_date)

    # TODO check if needed
    # @api.constrains('state', 'journal_id', 'to_pay_amount')
    # def check_journal_amount_restriction_with_double_validation(self):
    #     """
    #     We add this constraint that lins double validation module and
    #     voucher reconcile
    #     """
    #     for voucher in self.filtered(lambda x: x.state == 'confirmed'):
    #         journal = self.journal_id
    #         if (
    #                 journal.voucher_amount_restriction == 'cant_be_cero' and
    #                 not voucher.to_pay_amount
    #         ):
    #             raise ValidationError(_(
    #                 "On Journal '%s' to pay amount can't be cero!\n"
    #                 "* Voucher id: %i") % (journal.name, voucher.id))
    #         elif (
    #                 journal.voucher_amount_restriction == 'must_be_cero' and
    #                 voucher.to_pay_amount
    #         ):
    #             raise ValidationError(_(
    #                 "On Journal '%s' to pay amount must be cero!\n"
    #                 "* Voucher id: %i") % (journal.name, voucher.id))
    #     return True

    # TODO enable
    # @api.one
    # def _get_paid_withholding(self):
    #     paid_move_ids = [
    #         x.move_line_id.move_id.id for x in self.line_ids if x.amount]
    #     paid_withholdings = self.env['account.voucher.withholding'].search([(
    #         'move_line_id.tax_settlement_move_id', 'in', paid_move_ids)])
    #     self.paid_withholding_ids = paid_withholdings

    @api.multi
    def to_signature_process(self):
        self.write({'state': 'signature_process'})

    @api.multi
    def to_signed(self):
        self.write({'state': 'signed'})

    @api.multi
    # dummy depends to compute values on create
    @api.depends('transaction_id')
    def get_user_locations(self):
        for rec in self:
            rec.user_location_ids = rec.env.user.location_ids

    @api.model
    def _search_budget_positions(self, operator, value):
        return [
            ('line_ids.move_line_id.invoice.invoice_line_ids.'
                'definitive_line_id.preventive_line_id.budget_position_id',
                operator, value)]

    @api.multi
    def _get_budget_positions_and_invoices(self):
        for rec in self:
            # si esta validado entonces las facturas son las macheadas, si no
            # las seleccionadas
            move_lines = rec.matched_move_line_ids or rec.to_pay_move_line_ids
            rec.invoice_ids = move_lines.mapped('invoice_id')
            rec.budget_position_ids = rec.invoice_ids.mapped(
                'invoice_line_ids.definitive_line_id.preventive_line_id.'
                'budget_position_id')

    @api.multi
    @api.depends(
        'transaction_id',
    )
    def _get_partners(self):
        _logger.info('Get partners from transaction')
        for rec in self:
            transaction = rec.transaction_id
            if transaction:
                if transaction.type_id.with_advance_payment and (
                        transaction.partner_id):
                    partners = transaction.partner_id.commercial_partner_id.id
                else:
                    partners = transaction.mapped(
                        'supplier_ids.commercial_partner_id')
                rec.partner_ids = partners

    @api.multi
    def _get_to_pay_move_lines_domain(self):
        """
        We add transaction to get_move_lines function
        """
        domain = super(
            AccountPaymentGroup, self)._get_to_pay_move_lines_domain()
        if self.transaction_id:
            domain.append(
                ('invoice_id.transaction_id', '=', self.transaction_id.id))
        return domain

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

# TODO ver si son necesarias o no y mover dependencia de sipreco_project
# a este
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

    @api.multi
    @api.constrains('state')
    def update_invoice_amounts(self):
        _logger.info('Updating invoice amounts from voucher')
        # when voucher state changes we recomputed related invoice values
        # we could improove this filtering by relevant states
        for rec in self:
            rec.invoice_ids.sudo()._compute_to_pay_amount()

    @api.multi
    @api.constrains('confirmation_date', 'payment_min_date')
    def check_date(self):
        _logger.info('Checking dates')
        for rec in self:
            if not rec.confirmation_date:
                continue
            for invoice in rec.invoice_ids:
                if rec.confirmation_date < invoice.date_invoice:
                    raise ValidationError(_(
                        'La fecha de confirmación no puede ser menor a la '
                        'fecha de la factura que se esta pagando'))
            if not rec.payment_date:
                continue
            if rec.payment_date < rec.confirmation_date:
                raise ValidationError(_(
                    'La fecha de validacion del pago no puede ser menor a la '
                    'fecha de confirmación'))

    @api.multi
    @api.constrains('unreconciled_amount', 'transaction_id', 'state')
    def check_voucher_transaction_amount(self):
        """
        """
        for rec in self:
            _logger.info('Checking transaction amount on voucher %s' % rec.id)
            if rec.transaction_with_advance_payment:
                # forzamos el recalculo porque al ser store no lo recalculaba
                rec.transaction_id._get_advance_remaining_amount()
                advance_remaining_amount = rec.currency_id.round(
                    rec.transaction_id.advance_remaining_amount)
                if advance_remaining_amount < 0.0:
                    raise ValidationError(_(
                        'In advance transactions, payment orders amount (%s) '
                        'can not be greater than transaction advance remaining'
                        ' amount (%s)') % (
                        rec.unreconciled_amount,
                        advance_remaining_amount + rec.unreconciled_amount))

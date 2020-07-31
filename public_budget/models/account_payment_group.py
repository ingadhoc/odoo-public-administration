from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class AccountPaymentGroup(models.Model):

    _inherit = 'account.payment.group'

    # We add signature states
    state = fields.Selection(
        selection_add=[
            ('draft', 'Borrador'),
            ('confirmed', 'Confirmado'),
            ('signature_process', 'En Proceso de Firma'),
            ('signed', 'Firmado'),
            # we also change posted for paid
            ('posted', 'Pagado'),
            ('cancel', 'Cancelled'),
        ])
    # agregamos reference que fue depreciado y estan acostumbrados a usar
    reference = fields.Char(
        string='Ref. pago',
    )
    budget_id = fields.Many2one(
        related='transaction_id.budget_id',
        store=True,
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        context={'default_type': 'payment'},
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
    )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
    )
    budget_position_ids = fields.Many2many(
        relation='voucher_position_rel',
        comodel_name='public_budget.budget_position',
        string='Partidas Relacionadas',
        help='Partidas Presupuestarias Relacionadas',
        compute='_compute_budget_positions_and_invoices',
        search='_search_budget_positions',
    )
    # lo agregamos por compatiblidad hacia atras y tmb porque es mas facil
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string='Facturas Relacionadas',
        compute='_compute_budget_positions_and_invoices'
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        compute='_compute_partners',
        string='Partners'
    )
    advance_request_id = fields.Many2one(
        'public_budget.advance_request',
        readonly=True,
    )
    transaction_with_advance_payment = fields.Boolean(
        store=True,
        related='transaction_id.type_id.with_advance_payment',
    )
    user_location_ids = fields.Many2many(
        compute='_compute_user_locations',
        comodel_name='public_budget.location',
        string='User Locations',
    )
    payment_base_date = fields.Date(
        string='Payment Base Date',
        readonly=True,
        # nos pidieron que no haya valor por defecto
        # default=fields.Date.context_today,
        states={'draft': [('readonly', False)]},
        help='Date used to calculate payment date',
    )
    payment_days = fields.Integer(
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Days added to payment base date to get the payment date',
    )
    days_interval_type = fields.Selection([
        ('business_days', 'Business Days'),
        ('calendar_days', 'Calendar Days')],
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='business_days',
    )
    payment_min_date = fields.Date(
        compute='_compute_payment_min_date',
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
    to_signature_date = fields.Date(
        'Fecha a Proceso de Firma',
        help='Fecha en la que fue pasado a proceso de firma. Utilizada para '
        'acumular retenciones.',
        states={
            'draft': [('readonly', False)],
            'confirmed': [('readonly', False)]},
        readonly=True,
        copy=False,
    )
    # hacemos que la fecha de pago no sea obligatoria ya que seteamos fecha
    # de validacion si no estaba seteada (al final en archivo a parte
    # _monkey_patch)
    payment_date = fields.Date(
        required=False,
        track_visibility='onchange',
        # al final, para evitar que la seteen equivocadamente, la dejamos
        # editable solo en isgnature y signed
        states={
            # 'draft': [('readonly', False)],
            # 'confirmed': [('readonly', False)],
            'signature_process': [('readonly', False)],
            'signed': [('readonly', False)],
        },
    )
    # TODO implementar
    # paid_withholding_ids = fields.Many2many(
    #     comodel_name='account.voucher.withholding',
    #     string='Retenciones Pagadas',
    #     help='Retenciones pagadas con este voucher',
    #     compute='_get_paid_withholding'
    # )
    show_print_receipt_button = fields.Boolean(
        _('Show Print Receipt Button'),
        compute='_compute_show_print_receipt_button',
    )
    withholding_line_ids = fields.Many2many(
        'account.move.line',
        compute='_compute_withholding_lines'
    )

    def _compute_withholding_lines(self):
        for rec in self:
            rec.withholding_line_ids = rec.move_line_ids.filtered(
                'tax_line_id')

    def post(self):
        for rec in self:
            # si no estaba seteada la setamos
            if not rec.payment_date:
                rec.payment_date = fields.Date.today()
            # idem para los payments
            # como ellos no ven el campo payment date tiene mas sentido
            # pisarlo (por ejemplo por si validaron y luego cancelaron para
            # corregir fecha o si setearon fecha antes de crear las lineas
            # en cuyo caso se completa con esa fecha y luego la pudieron
            # cambiar) TODO faltaria contemplar el caso de cheques cambiados
            # porque por ahí sobre-escribimos una fecha (si se canceló el pago)
            # y se re-abrió (igualmente es dificil porque no se pueden cancelar
            # así nomas pagos con cheques cambiados
            rec.payment_ids.write({'payment_date': rec.payment_date})
            # rec.payment_ids.filtered(lambda x: not x.payment_date).write(
            #     {'payment_date': rec.payment_date})
            if (
                    rec.expedient_id and rec.expedient_id.current_location_id
                    not in rec.user_location_ids):
                raise ValidationError(_(
                    'No puede validar un pago si el expediente no está en '
                    'una ubicación autorizada para ústed'))
        return super(AccountPaymentGroup, self.with_context(is_recipt=True)).post()

    # las seteamos directamente al postear total antes no se usan
    # @api.constrains('payment_date')
    # def update_payment_date(self):
    #     for rec in self:
    #         rec.payment_ids.write({'payment_date': rec.payment_date})

    def unlink(self):
        if self.filtered('document_number'):
            raise ValidationError(_(
                'No puede borrar una orden de pago que ya fue numerada'))
        return super().unlink()

    def confirm(self):
        for rec in self:
            msg = _('It is not possible'
                    ' to confirm a payment if the payment'
                    ' expedient is not in a users'
                    ' allowed location or is in transit')
            rec.expedient_id and rec.expedient_id.\
                check_location_allowed_for_current_user(msg)

            if not rec.payment_base_date:
                raise ValidationError(_(
                    'No puede confirmar una orden de pago sin fecha base de '
                    'pago'))
            # si hay devoluciones entonces si se puede confirmar sin importe
            if not rec.to_pay_amount and not rec.payment_ids.mapped(
                    'returned_payment_ids'):
                raise ValidationError(_(
                    'No puede confirmar una orden de pago sin importe a pagar')
                )
            if not rec.confirmation_date:
                rec.confirmation_date = fields.Date.today()
            # si bien este control lo podría hacer el mimso invoice cuando
            # se calcula el to_pay_amount (ya que se estaría mandando a pagar)
            # más de lo permitodo, en realidad el método de mandado a pagar,
            # si la factura está paga, considera el monto de factura para
            # por temas de performance y para ser más robusto por si se
            # pierde el link de to pay lines del pago
            already_paying = self.transaction_id.payment_group_ids.filtered(
                lambda x: x.state not in ['cancel', 'draft'] and x != self
            ).mapped('to_pay_move_line_ids')
            if rec.to_pay_move_line_ids & already_paying:
                raise ValidationError(_(
                    'No puede mandar a pagar líneas que ya se mandaron a '
                    'pagar'))
            # In this case remove all followers when confirm a payment
            rec.message_unsubscribe(partner_ids=rec.message_partner_ids.ids)
        return super().confirm()

    def _get_receiptbook(self):
        # we dont want any receiptbook as default
        return False

    @api.depends('payment_ids.check_ids.state', 'state')
    def _compute_show_print_receipt_button(self):
        for rec in self:
            show_print_receipt_button = False

            not_handed_checks = rec.payment_ids.mapped('check_ids').filtered(
                lambda r: r.state in (
                    'holding', 'to_be_handed'))

            if rec.state == 'posted' and not not_handed_checks:
                show_print_receipt_button = True
            rec.show_print_receipt_button = show_print_receipt_button

    @api.depends('payment_base_date', 'payment_days', 'days_interval_type')
    def _compute_payment_min_date(self):
        for rec in self:
            current_date = False
            business_days_to_add = rec.payment_days
            if rec.payment_base_date:
                if rec.days_interval_type == 'business_days':
                    current_date = fields.Date.from_string(
                        rec.payment_base_date)
                    while business_days_to_add > 0:
                        current_date = current_date + relativedelta(days=1)
                        weekday = current_date.weekday()
                        # sunday = 6
                        if weekday >= 5 or self.env[
                                'hr.holidays.public'].is_public_holiday(
                                    current_date):
                            continue
                        # if current_date in holidays:
                        #     continue
                        business_days_to_add -= 1
                else:
                    current_date = fields.Date.from_string(
                        rec.payment_base_date)
                    current_date = current_date + relativedelta(
                        days=rec.payment_days)

                # además hacemos que la fecha mínima no pueda ser día no habil
                # sin Importar si el intervalo debe
                #  considerar días habiles o no
                while current_date.weekday() >= 5 or self.env[
                        'hr.holidays.public'].is_public_holiday(
                            current_date):
                    current_date = current_date + relativedelta(days=1)
            rec.payment_min_date = fields.Date.to_string(current_date)

    # TODO enable
    # def _get_paid_withholding(self):
    #     paid_move_ids = [
    #         x.move_line_id.move_id.id for x in self.line_ids if x.amount]
    #     paid_withholdings = self.env['account.voucher.withholding'].search([(
    #         'move_line_id.tax_settlement_move_id', 'in', paid_move_ids)])
    #     self.paid_withholding_ids = paid_withholdings

    def to_signature_process(self):
        for rec in self:
            for payment in rec.payment_ids.filtered(
                    lambda x: x.payment_method_code == 'issue_check'):
                if not payment.check_number or not payment.check_name:
                    raise ValidationError(_(
                        'Para mandar a proceso de firma debe definir número '
                        'de cheque en cada línea de pago.\n'
                        '* ID de orden de pago: %s' % rec.id))

            if rec.currency_id.round(rec.payments_amount - rec.to_pay_amount):
                raise ValidationError(_(
                    'No puede mandar a pagar una orden de pago que tiene '
                    'Importe a pagar distinto a Importe de los Pagos'))
            rec.state = 'signature_process'
            if not rec.to_signature_date:
                rec.to_signature_date = fields.Date.today()

    def to_signed(self):
        self.write({'state': 'signed'})

    def back_to_confirmed(self):
        self.write({'state': 'confirmed'})

    # dummy depends to compute values on create
    @api.depends('transaction_id')
    def _compute_user_locations(self):
        for rec in self:
            rec.user_location_ids = rec.env.user.location_ids

    @api.model
    def _search_budget_positions(self, operator, value):
        return [
            ('to_pay_move_line_ids.move_id.invoice_move_ids.'
                'definitive_line_id.preventive_line_id.budget_position_id',
                operator, value)]

    def _compute_budget_positions_and_invoices(self):
        for rec in self:
            # si esta validado entonces las facturas son las macheadas, si no
            # las seleccionadas
            move_lines = rec.matched_move_line_ids or rec.to_pay_move_line_ids
            rec.invoice_ids = move_lines.mapped('move_id')
            rec.budget_position_ids = rec.invoice_ids.mapped(
                'invoice_line_ids.definitive_line_id.preventive_line_id.'
                'budget_position_id')

    @api.depends(
        'transaction_id',
    )
    def _compute_partners(self):
        _logger.info('Get partners from transaction')
        for rec in self:
            rec.partner_ids = self.env['res.partner']
            transaction = rec.transaction_id
            if transaction:
                if transaction.type_id.with_advance_payment and (
                        transaction.partner_id):
                    # no hace falta que sea el comercial...
                    partners = transaction.partner_id
                    # partners = transaction.partner_id.commercial_partner_id
                else:
                    # no hace falta que sea el comercial...
                    partners = transaction.mapped(
                        # 'supplier_ids.commercial_partner_id')
                        'supplier_ids')
                rec.partner_ids = partners

    def _get_to_pay_move_lines_domain(self):
        """
        We add transaction to get_move_lines function
        """
        domain = super()._get_to_pay_move_lines_domain()
        if self.transaction_id:
            # con esto validamos que no se haya mandado a pagar en otra
            # orden de pago (si dejamos si está cancelada)
            already_paying = self.transaction_id.payment_group_ids.filtered(
                lambda x: x.state != 'cancel').mapped('to_pay_move_line_ids')
            domain.extend([
                ('move_id.transaction_id', '=', self.transaction_id.id),
                ('id', 'not in', already_paying.ids)])
        return domain

    # modificamos estas funciones para que si esta en borrador no setee ningun
    # valor por defecto
    @api.onchange('company_regimenes_ganancias_ids')
    def change_company_regimenes_ganancias(self):
        if (
                self.state != 'draft' and
                self.company_regimenes_ganancias_ids and
                self.partner_type == 'supplier'):
            self.retencion_ganancias = 'nro_regimen'

    @api.constrains('state')
    def update_invoice_amounts(self):
        _logger.info('Updating invoice amounts from payment group')
        # when payment state changes we recomputed related invoice values
        # we could improove this filtering by relevant states
        for rec in self:
            rec.invoice_ids.sudo()._compute_to_pay_amount()

    @api.constrains('confirmation_date', 'payment_min_date', 'payment_date')
    def check_dates(self):
        _logger.info('Checking dates')
        for rec in self:
            if not rec.confirmation_date:
                continue
            for invoice in rec.invoice_ids:
                if rec.confirmation_date < invoice.invoice_date:
                    raise ValidationError(_(
                        'La fecha de confirmación no puede ser menor a la '
                        'fecha de la factura que se esta pagando.\n'
                        '* Id Factura / Fecha: %s - %s\n'
                        '* Id Pago / Fecha Confirmación: %s - %s') % (
                        invoice.id, invoice.invoice_date,
                        rec.id, rec.confirmation_date))
            if not rec.payment_date:
                continue
            if rec.payment_date > fields.Date.context_today(rec):
                raise ValidationError(_(
                    'No puede usar una fecha de pago superior a hoy'))
            if rec.payment_date < rec.confirmation_date:
                raise ValidationError(_(
                    'La fecha de validacion del pago no puede ser menor a la '
                    'fecha de confirmación.\n'
                    '* Id de Pago: %s\n'
                    '* Fecha de pago: %s\n'
                    '* Fecha de confirmación: %s\n' % (
                        rec.id, rec.payment_date, rec.confirmation_date)))
            if rec.payment_date < rec.payment_min_date:
                raise ValidationError(_(
                    'La fecha de validacion del pago no puede ser menor a la '
                    'fecha mínima de pago\n'
                    '* Id de Pago: %s\n'
                    '* Fecha de pago: %s\n'
                    '* Fecha mínima de pago: %s\n' % (
                        rec.id, rec.payment_date, rec.payment_min_date)))

    @api.constrains('unreconciled_amount', 'transaction_id', 'state')
    def check_avance_transaction_amount(self):
        """
        """
        for rec in self.filtered('transaction_with_advance_payment'):
            _logger.info('Checking transaction amount on voucher %s' % rec.id)
            # forzamos el recalculo porque al ser store no lo recalculaba
            rec.transaction_id._compute_advance_remaining_amount()
            advance_remaining_amount = rec.currency_id.round(
                rec.transaction_id.advance_remaining_amount)
            if advance_remaining_amount < 0.0:
                raise ValidationError(_(
                    'In advance transactions, payment orders amount (%s) '
                    'can not be greater than transaction advance remaining'
                    ' amount (%s)') % (
                    rec.unreconciled_amount,
                    advance_remaining_amount + rec.unreconciled_amount))

    @api.constrains('receiptbook_id')
    def set_document_number(self):
        """
        Quieren que en caunto se cree, si tiene talonario, se asigne número
        """
        for rec in self.filtered(
            lambda x: x.receiptbook_id.sequence_id and
                not x.document_number).with_context(is_recipt=True):
            rec.document_number = (
                rec.receiptbook_id.sequence_id.next_by_id())

    def _compute_name(self):
        """
        Agregamos numero de documento en todos los estados (no solo posteado)
        """
        res = super()._compute_name()
        for rec in self.filtered(lambda x: x.state != 'posted'):
            if rec.document_number and rec.document_type_id:
                rec.name = ("%s%s" % (
                    rec.document_type_id.doc_code_prefix or '',
                    rec.document_number))
        return res

    def action_aeroo_certificado_de_retencion_report(self):
        self.ensure_one()
        payments = self.payment_ids.filtered(
            lambda x:
            x.payment_method_code == 'withholding' and x.partner_type ==
            'supplier')
        if not payments:
            return False
        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'l10n_ar_account_withholding.report_withholding_certificate')],
            limit=1).report_action(payments)

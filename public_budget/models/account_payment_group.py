import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    # We add signature states
    state = fields.Selection(
        selection_add=[
            ("draft", "Draft"),
            ("in_process", "In Process"),
            ("confirmed", "Confirmado"),  # new
            ("signature_process", "En Proceso de Firma"),  # new
            ("signed", "Firmado"),  # new
            ("paid", "Paid"),
            ("canceled", "Canceled"),
            ("rejected", "Rejected"),
        ],
        ondelete={"confirmed": "set draft", "signature_process": "set draft", "signed": "set draft"},
    )
    # agregamos reference que fue depreciado y estan acostumbrados a usar
    reference = fields.Char(
        string="Ref. pago",
    )
    budget_id = fields.Many2one(
        related="transaction_id.budget_id",
        store=True,
    )
    expedient_id = fields.Many2one(
        "public_budget.expedient",
        context={"default_type": "payment"},
        # states={'draft': [('readonly', False)]},
        ondelete="restrict",
    )
    transaction_id = fields.Many2one(
        "public_budget.transaction",
    )
    budget_position_ids = fields.Many2many(
        comodel_name="public_budget.budget_position",
        string="Partidas Relacionadas",
        help="Partidas Presupuestarias Relacionadas",
        compute="_compute_budget_positions_and_invoices",
        search="_search_budget_positions",
    )
    # lo agregamos por compatiblidad hacia atras y tmb porque es mas facil
    public_invoice_ids = fields.Many2many(
        comodel_name="account.move", string="Facturas Relacionadas", compute="_compute_budget_positions_and_invoices"
    )
    partner_ids = fields.Many2many(comodel_name="res.partner", compute="_compute_partners", string="Partners")
    advance_request_id = fields.Many2one(
        "public_budget.advance_request",
        readonly=True,
    )
    transaction_with_advance_payment = fields.Boolean(
        store=True,
        related="transaction_id.type_id.with_advance_payment",
    )
    user_location_ids = fields.Many2many(
        compute="_compute_user_locations",
        comodel_name="public_budget.location",
        string="User Locations",
    )
    payment_base_date = fields.Datetime(
        string="Payment Base Date",
        # nos pidieron que no haya valor por defecto
        # default=fields.Date.context_today,
        # states={'draft': [('readonly', False)]},
        help="Date used to calculate payment date",
    )
    payment_days = fields.Integer(
        # states={'draft': [('readonly', False)]},
        help="Days added to payment base date to get the payment date",
    )
    days_interval_type = fields.Selection(
        [("business_days", "Business Days"), ("calendar_days", "Calendar Days")],
        # states={'draft': [('readonly', False)]},
        default="business_days",
    )
    payment_min_date = fields.Date(
        compute="_compute_payment_min_date",
        string="Fecha Min. de Pago",
        help="El pago no puede ser validado antes de esta fecha",
        store=True,
        readonly=False,
    )
    confirmation_date = fields.Date(
        "Fecha de Confirmación",
        # states={'draft': [('readonly', False)]},
        copy=False,
    )
    to_signature_date = fields.Date(
        "Fecha a Proceso de Firma",
        help="Fecha en la que fue pasado a proceso de firma. Utilizada para acumular retenciones.",
        # states={
        #     'draft': [('readonly', False)],
        #     'confirmed': [('readonly', False)]},
        copy=False,
    )
    date = fields.Date(
        required=False,
        string="Payment Date",
    )
    # TODO implementar
    # paid_withholding_ids = fields.Many2many(
    #     comodel_name='account.voucher.withholding',
    #     string='Retenciones Pagadas',
    #     help='Retenciones pagadas con este voucher',
    #     compute='_get_paid_withholding'
    # )

    @api.model
    def default_get(self, fields):
        """hacemos que la fecha de pago no sea required ya que seteamos fecha de validacion si no estaba seteada"""
        vals = super().default_get(fields)
        vals["date"] = False
        return vals

    def post(self):
        for rec in self:
            # si no estaba seteada la setamos
            if not rec.date:
                rec.date = fields.Date.today()
            # idem para los payments
            # como ellos no ven el campo payment date tiene mas sentido
            # pisarlo (por ejemplo por si validaron y luego cancelaron para
            # corregir fecha o si setearon fecha antes de crear las lineas
            # en cuyo caso se completa con esa fecha y luego la pudieron
            # cambiar) TODO faltaria contemplar el caso de cheques cambiados
            # porque por ahí sobre-escribimos una fecha (si se canceló el pago)
            # y se re-abrió (igualmente es dificil porque no se pueden cancelar
            # así nomas pagos con cheques cambiados
            for pay in rec.payment_ids:
                if not pay.date:
                    pay.write({"date": rec.date})
            # rec.payment_ids.filtered(lambda x: not x.date).write(
            #     {'date': rec.date})
            if rec.expedient_id and rec.expedient_id.current_location_id not in rec.user_location_ids:
                raise ValidationError(
                    _("No puede validar un pago si el expediente no está en una ubicación autorizada para ústed")
                )
        return super(AccountPayment, self.with_context(is_recipt=True)).post()

    def unlink(self):
        if self.filtered("name") and not self.env.context.get("force_delete"):
            raise ValidationError(_("No puede borrar una orden de pago que ya fue numerada"))
        return super().unlink()

    def confirm(self):
        for rec in self:
            msg = _(
                "It is not possible"
                " to confirm a payment if the payment"
                " expedient is not in a users"
                " allowed location or is in transit"
            )
            rec.expedient_id and rec.expedient_id.check_location_allowed_for_current_user(msg)

            if not rec.payment_base_date:
                raise ValidationError(_("No puede confirmar una orden de pago sin fecha base de pago"))
            # si hay devoluciones entonces si se puede confirmar sin importe
            if not rec.to_pay_amount and not rec.payment_ids.mapped("returned_payment_ids"):
                raise ValidationError(_("No puede confirmar una orden de pago sin importe a pagar"))
            if not rec.confirmation_date:
                rec.confirmation_date = fields.Date.today()
            # si bien este control lo podría hacer el mimso invoice cuando
            # se calcula el to_pay_amount (ya que se estaría mandando a pagar)
            # más de lo permitodo, en realidad el método de mandado a pagar,
            # si la factura está paga, considera el monto de factura para
            # por temas de performance y para ser más robusto por si se
            # pierde el link de to pay lines del pago
            already_paying = self.transaction_id.payment_ids.filtered(
                lambda x: x.state not in ["cancel", "draft"] and x != self
            ).mapped("to_pay_move_line_ids")
            if rec.to_pay_move_line_ids & already_paying:
                raise ValidationError(_("No puede mandar a pagar líneas que ya se mandaron a pagar"))
            # In this case remove all followers when confirm a payment
            rec.message_unsubscribe(partner_ids=rec.message_partner_ids.ids)
        return super().confirm()

    def _get_receiptbook(self):
        # we dont want any receiptbook as default
        return False

    @api.depends("payment_base_date", "payment_days", "days_interval_type")
    def _compute_payment_min_date(self):
        for rec in self:
            # return
            current_date = False
            if rec.payment_base_date:
                if rec.days_interval_type == "business_days":
                    current_date = rec.company_id.resource_calendar_id.plan_days(
                        rec.payment_days, rec.payment_base_date, compute_leaves=True
                    )
                else:
                    current_date = rec.payment_base_date + relativedelta(days=rec.payment_days)
                    # por mas que no sean business days, si la fecha no es laborable tomamos el proximo dia
                    current_date = rec.company_id.resource_calendar_id.plan_hours(
                        hours=1 / 3600.0,  # 1 segundo
                        day_dt=current_date,
                        compute_leaves=True,
                    )

            rec.payment_min_date = current_date

    # TODO enable
    # def _get_paid_withholding(self):
    #     paid_move_ids = [
    #         x.move_line_id.move_id.id for x in self.line_ids if x.amount]
    #     paid_withholdings = self.env['account.voucher.withholding'].search([(
    #         'move_line_id.tax_settlement_move_id', 'in', paid_move_ids)])
    #     self.paid_withholding_ids = paid_withholdings

    def to_signature_process(self):
        for rec in self:
            if rec.currency_id.round(rec.payment_total - rec.to_pay_amount):
                raise ValidationError(
                    _(
                        "No puede mandar a pagar una orden de pago que tiene "
                        "Importe a pagar distinto a Importe de los Pagos"
                    )
                )
            rec.state = "signature_process"
            if not rec.to_signature_date:
                rec.to_signature_date = fields.Date.today()

    def to_signed(self):
        self.write({"state": "signed"})

    def back_to_confirmed(self):
        self.write({"state": "confirmed"})

    # dummy depends to compute values on create
    @api.depends("transaction_id")
    def _compute_user_locations(self):
        for rec in self:
            rec.user_location_ids = rec.env.user.location_ids

    @api.model
    def _search_budget_positions(self, operator, value):
        return [
            (
                "to_pay_move_line_ids.move_id.invoice_line_ids."
                "definitive_line_id.preventive_line_id.budget_position_id",
                operator,
                value,
            )
        ]

    def _compute_budget_positions_and_invoices(self):
        for rec in self:
            # si esta validado entonces las facturas son las macheadas, si no
            # las seleccionadas
            move_lines = rec.matched_move_line_ids or rec.to_pay_move_line_ids
            rec.public_invoice_ids = move_lines.mapped("move_id").filtered(lambda m: m.is_invoice())
            rec.budget_position_ids = rec.public_invoice_ids.mapped(
                "invoice_line_ids.definitive_line_id.preventive_line_id.budget_position_id"
            )

    @api.depends(
        "transaction_id",
    )
    def _compute_partners(self):
        _logger.info("Get partners from transaction")
        for rec in self:
            rec.partner_ids = self.env["res.partner"]
            transaction = rec.transaction_id
            if transaction:
                if transaction.type_id.with_advance_payment and (transaction.partner_id):
                    # no hace falta que sea el comercial...
                    partners = transaction.partner_id
                    # partners = transaction.partner_id.commercial_partner_id
                else:
                    # no hace falta que sea el comercial...
                    partners = transaction.mapped(
                        # 'supplier_ids.commercial_partner_id')
                        "supplier_ids"
                    )
                rec.partner_ids = partners

    def _get_to_pay_move_lines_domain(self):
        """
        We add transaction to get_move_lines function
        """
        domain = super()._get_to_pay_move_lines_domain()
        if self.transaction_id:
            # con esto validamos que no se haya mandado a pagar en otra
            # orden de pago (si dejamos si está cancelada)
            already_paying = self.transaction_id.payment_ids.filtered(lambda x: x.state != "cancel").mapped(
                "to_pay_move_line_ids"
            )
            domain.extend(
                [("move_id.transaction_id", "=", self.transaction_id.id), ("id", "not in", already_paying.ids)]
            )
        return domain

    @api.constrains("state")
    def update_invoice_amounts(self):
        _logger.info("Updating invoice amounts from payment group")
        # when payment state changes we recomputed related invoice values
        # we could improove this filtering by relevant states
        for rec in self:
            rec.public_invoice_ids.sudo()._compute_to_pay_amount()

    @api.constrains("confirmation_date", "payment_min_date", "date")
    def check_dates(self):
        _logger.info("Checking dates")
        for rec in self:
            if not rec.confirmation_date:
                continue
            for invoice in rec.public_invoice_ids:
                if rec.confirmation_date < invoice.invoice_date:
                    raise ValidationError(
                        _(
                            "La fecha de confirmación no puede ser menor a la "
                            "fecha de la factura que se esta pagando.\n"
                            "* Id Factura / Fecha: %s - %s\n"
                            "* Id Pago / Fecha Confirmación: %s - %s"
                        )
                        % (invoice.id, invoice.invoice_date, rec.id, rec.confirmation_date)
                    )
            if not rec.date:
                continue
            if rec.date > fields.Date.context_today(rec):
                raise ValidationError(_("No puede usar una fecha de pago superior a hoy"))
            if rec.date < rec.confirmation_date:
                raise ValidationError(
                    _(
                        "La fecha de validacion del pago no puede ser menor a la "
                        "fecha de confirmación.\n"
                        "* Id de Pago: %s\n"
                        "* Fecha de pago: %s\n"
                        "* Fecha de confirmación: %s\n" % (rec.id, rec.date, rec.confirmation_date)
                    )
                )
            if rec.date < rec.payment_min_date:
                raise ValidationError(
                    _(
                        "La fecha de validacion del pago no puede ser menor a la "
                        "fecha mínima de pago\n"
                        "* Id de Pago: %s\n"
                        "* Fecha de pago: %s\n"
                        "* Fecha mínima de pago: %s\n" % (rec.id, rec.date, rec.payment_min_date)
                    )
                )

    @api.constrains("unreconciled_amount", "transaction_id", "state")
    def check_avance_transaction_amount(self):
        """ """
        for rec in self.filtered("transaction_with_advance_payment"):
            _logger.info("Checking transaction amount on voucher %s" % rec.id)
            # forzamos el recalculo porque al ser store no lo recalculaba
            rec.transaction_id._compute_advance_remaining_amount()
            advance_remaining_amount = rec.currency_id.round(rec.transaction_id.advance_remaining_amount)
            if advance_remaining_amount < 0.0:
                raise ValidationError(
                    _(
                        "In advance transactions, payment orders amount (%s) "
                        "can not be greater than transaction advance remaining"
                        " amount (%s)"
                    )
                    % (rec.unreconciled_amount, advance_remaining_amount + rec.unreconciled_amount)
                )

    @api.model_create_multi
    def create(self, vals_list):
        """
        When the payment group is created, assing document number.
        """
        recs = super().create(vals_list)
        for rec in recs:
            if rec.receiptbook_id.sequence_id and not (rec.name or rec.name == "/"):
                rec = rec.with_context(is_recipt=True)
                rec.name = rec.receiptbook_id.with_context(ir_sequence_date=rec.date).sequence_id.next_by_id()
                # TODO revisar si tenemos que agregar prefijo. de agregarlo tmb tenemos que hacerlo en el write de abajo
                # rec.name = "%s %s" % (rec.receiptbook_id.document_type_id.doc_code_prefix, name)

        return recs

    def write(self, vals):
        """
        When the payment group is updated and without document number, assing document number.
        """
        res = super().write(vals)
        if vals.get("receiptbook_id", False):
            for rec in self.filtered(
                lambda p: p.receiptbook_id.sequence_id and not (p.name or p.name == "/")
            ).with_context(is_recipt=True):
                rec.name = rec.receiptbook_id.with_context(ir_sequence_date=rec.date).sequence_id.next_by_id()
        return res

    def action_aeroo_certificado_de_retencion_report(self):
        self.ensure_one()
        return self.env.ref("l10n_ar_tax.action_report_withholding_certificate").report_action(
            self.l10n_ar_withholding_line_ids.ids
        )

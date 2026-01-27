import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    # We add signature states
    # ahora que el campo es almacenado podríamos unificar y en casi todos lados estandarizar y usar "sipreco_state"
    # tmb podriamos re-evaluar volver a heredar "state" y erradicar estos dos campos
    sipreco_state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("confirmed", "Confirmado"),  # new
            ("signature_process", "En Proceso de Firma"),  # new
            ("signed", "Firmado"),  # new
            ("in_process", "Pagado (NR)"),
            ("paid", "Pagado"),
            ("canceled", "Cancelado"),
            ("rejected", "Rechazado"),
        ],
        compute='_compute_sipreco_state',
        store=True,
    )
    # We add signature states
    approval_state = fields.Selection(
        selection=[
            ("confirmed", "Confirmado"),  # new
            ("signature_process", "En Proceso de Firma"),  # new
            ("signed", "Firmado"),  # new
        ],
    )
    # agregamos reference que fue depreciado y estan acostumbrados a usar
    reference = fields.Char(
        string="Ref. pago",
    )
    budget_id = fields.Many2one(
        related="transaction_id.budget_id",
        store=True,
        string="Presupuesto",
    )
    expedient_id = fields.Many2one(
        "public_budget.expedient",
        context={"default_type": "payment"},
        ondelete="restrict",
        string="Expediente",
    )
    transaction_id = fields.Many2one(
        "public_budget.transaction",
        string="Transacción",
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
        help="Date used to calculate payment date",
    )
    payment_days = fields.Integer(
        help="Days added to payment base date to get the payment date",
    )
    days_interval_type = fields.Selection(
        [("business_days", "Business Days"), ("calendar_days", "Calendar Days")],
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
        copy=False,
    )
    to_signature_date = fields.Date(
        "Fecha a Proceso de Firma",
        help="Fecha en la que fue pasado a proceso de firma. Utilizada para acumular retenciones.",
        copy=False,
    )
    date = fields.Date(
        required=False,
        string="Payment Date",
    )

    @api.depends('approval_state', 'state')
    def _compute_sipreco_state(self):
        for rec in self:
            if rec.state == 'draft':
                rec.sipreco_state = rec.approval_state or 'draft'
            else:
                rec.sipreco_state = rec.state

    @api.model
    def default_get(self, fields):
        """hacemos que la fecha de pago no sea required ya que seteamos fecha de validacion si no estaba seteada"""
        vals = super().default_get(fields)
        vals["date"] = False
        return vals

    def action_post(self):
        for rec in self:
            # si no estaba seteada la setamos
            if not rec.date:
                rec.date = fields.Date.today()
            if not self.env.context.get('skip_location_validation', False) and rec.expedient_id and rec.expedient_id.current_location_id not in rec.user_location_ids:
                raise ValidationError(
                    _("No puede validar un pago si el expediente no está en una ubicación autorizada para ústed")
                )
        return super(AccountPayment, self.with_context(is_recipt=True)).action_post()

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
            if not rec.to_pay_amount and not rec.mapped("returned_payment_ids"):
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
                lambda x: x.state not in ["canceled", "draft"] and x != self
            ).mapped("to_pay_move_line_ids")
            if rec.to_pay_move_line_ids & already_paying:
                raise ValidationError(_("No puede mandar a pagar líneas que ya se mandaron a pagar"))
            # In this case remove all followers when confirm a payment
            rec.message_unsubscribe(partner_ids=rec.message_partner_ids.ids)
            rec.approval_state = 'confirmed'

    def _get_receiptbook(self):
        # we dont want any receiptbook as default
        return False

    @api.depends("payment_base_date", "payment_days", "days_interval_type")
    def _compute_payment_min_date(self):
        for rec in self:
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

    def to_signature_process(self):
        for rec in self:
            if rec.currency_id.round(rec.payment_total - rec.to_pay_amount):
                raise ValidationError(
                    _(
                        "No puede mandar a pagar una orden de pago que tiene "
                        "Importe a pagar distinto a Importe de los Pagos"
                    )
                )
            rec.approval_state = "signature_process"
            if not rec.to_signature_date:
                rec.to_signature_date = fields.Date.today()

    def to_signed(self):
        self.write({"approval_state": "signed"})

    def back_to_confirmed(self):
        self.write({"approval_state": "confirmed"})

    def action_draft(self):
        self.write({"approval_state": False})
        return super().action_draft()

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
                else:
                    # no hace falta que sea el comercial...
                    partners = transaction.mapped(
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
            already_paying = (self.transaction_id.payment_ids - self).filtered(lambda x: x.state != "canceled").mapped(
                "to_pay_move_line_ids"
            )
            domain.extend(
                [("move_id.transaction_id", "=", self.transaction_id.id), ("id", "not in", already_paying.ids)]
            )
        return domain

    @api.constrains("state", "approval_state")
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

    @api.constrains("unreconciled_amount", "transaction_id", "state", "approval_state")
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

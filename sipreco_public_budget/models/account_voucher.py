# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class account_voucher(models.Model):
    _inherit = "account.voucher"

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
    net_amount = fields.Monetary(
        states={'confirmed': [('readonly', False)]}
    )
    issued_check_ids = fields.One2many(
        states={'confirmed': [('readonly', False)]}
    )
    withholding_ids = fields.One2many(
        states={'confirmed': [('readonly', False)]}
    )
    show_print_receipt_button = fields.Boolean(
        _('Show Print Receipt Button'),
        compute='get_show_print_receipt_button',
    )
    paid_withholding_ids = fields.Many2many(
        comodel_name='account.voucher.withholding',
        string='Retenciones Pagadas',
        help='Retenciones pagadas con este voucher',
        compute='_get_paid_withholding'
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
    def _get_paid_withholding(self):
        paid_move_ids = [
            x.move_line_id.move_id.id for x in self.line_ids if x.amount]
        paid_withholdings = self.env['account.voucher.withholding'].search([(
            'move_line_id.tax_settlement_move_id', 'in', paid_move_ids)])
        self.paid_withholding_ids = paid_withholdings

    @api.one
    @api.depends('issued_check_ids.state', 'state')
    def get_show_print_receipt_button(self):
        show_print_receipt_button = False
        not_handed_checks = self.issued_check_ids.filtered(
            lambda r: r.state not in ('handed', 'returned', 'debited'))
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

    # no need for this, dlete if needed
    # @api.constrains('state', 'journal_id', 'amount')
    # def check_journal_amount_restriction(self):
    #     """
    #     We overwrrite 'account_voucher_constraint' function to check also
    #     for "to signature" state
    #     """
    #     for voucher in self.filtered(
    #             lambda x: x.state in ['posted', 'signature_process']):
    #         journal = self.journal_id
    #         if (
    #                 journal.voucher_amount_restriction == 'cant_be_cero' and
    #                 not voucher.amount
    #                 ):
    #             raise ValidationError(_(
    #                 "On Journal '%s' amount can't be cero!\n"
    #                 "* Voucher id: %i") % (journal.name, voucher.id))
    #         elif (
    #                 journal.voucher_amount_restriction == 'must_be_cero' and
    #                 voucher.amount
    #                 ):
    #             raise ValidationError(_(
    #                 "On Journal '%s' amount must be cero!\n"
    #                 "* Voucher id: %i") % (journal.name, voucher.id))
    #     return True

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

# We add signature states

    state = fields.Selection(
        selection=[
            ('draft', _('Boorador')),
            ('confirmed', _('Confirmado')),
            ('signature_process', _('En Proceso de Firma')),
            ('signed', _('Firmado')),
            ('cancel', _('Cancelado')),
            ('proforma', _('Pro-forma')),
            # we also change posted for paid
            ('posted', _('Pagado'))
        ])

    @api.multi
    def check_to_sign_process(self):
        """
        """
        for voucher in self:
            if self.currency_id.round(voucher.amount - voucher.to_pay_amount):
                raise ValidationError(_('You can not send to sign process a Voucher \
                    that has Total Amount different from To Pay Amount'))
        return True

    # modificamos estas funciones para que si esta en borrador no setee ningun
    # valor por defecto
    @api.onchange('retencion_ganancias', 'partner_id_copy')
    def change_retencion_ganancias(self):
        def_regimen = False
        if self.state != 'draft' and self.retencion_ganancias == 'nro_regimen':
            cia_regs = self.company_regimenes_ganancias_ids
            partner_regimen = self.partner_id.default_regimen_ganancias_id
            if partner_regimen and partner_regimen in cia_regs:
                def_regimen = partner_regimen
            elif cia_regs:
                def_regimen = cia_regs[0]
        self.regimen_ganancias_id = def_regimen

    @api.onchange('company_regimenes_ganancias_ids')
    def change_company_regimenes_ganancias(self):
        if (
                self.state != 'draft' and
                self.company_regimenes_ganancias_ids and
                self.type == 'payment'):
            self.retencion_ganancias = 'nro_regimen'

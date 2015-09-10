# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
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
        states={},
        store=True,
        )
    net_amount = fields.Float(
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
        string=_('Paid Withholdings'),
        help=_('Withholding being paid with this voucher'),
        compute='_get_paid_withholding'
        )

    @api.model
    def create(self, vals):
        """
        we use force number as a hack to compute document number on creation
        """
        voucher_type = vals.get(
            'type', self._context.get('default_type', False))
        receiptbook = self.receiptbook_id.browse(
            vals.get('receiptbook_id', False))
        if receiptbook and voucher_type == 'payment':
            force_number = self.env['ir.sequence'].next_by_id(
                    receiptbook.sequence_id.id)
            vals['force_number'] = force_number
        return super(account_voucher, self).create(vals)

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
                if weekday >= 5:    # sunday = 6
                    continue
                # if current_date in holidays:
                #     continue
                business_days_to_add -= 1
        self.payment_date = current_date

    @api.constrains('state', 'to_pay_amount')
    def check_to_pay_amount(self):
        for voucher in self:
            if self.state == 'confirmed' and not voucher.to_pay_amount:
                raise Warning(_('You can not confirm a voucher with to pay\
                    amount equal to 0'))
        return True

# We add signature states

    state = fields.Selection(
        selection=[
            ('draft', _('Draft')),
            ('confirmed', _('Confirmed')),
            ('signature_process', _('Signature Process')),
            ('signed', _('Signed')),
            ('cancel', _('Cancelled')),
            ('proforma', _('Pro-forma')),
            # we also change posted for paid
            ('posted', _('Paid'))
        ])

    @api.multi
    def check_to_sign_process(self):
        """
        """
        for voucher in self:
            if voucher.amount != voucher.to_pay_amount:
                raise Warning(_('You can not send to sign process a Voucher \
                    that has Total Amount different from To Pay Amount'))
        return True

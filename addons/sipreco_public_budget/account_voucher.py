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

    @api.one
    @api.depends('payment_base_date', 'payment_days')
    def get_payment_date(self):
        payment_date = False
        if self.payment_base_date:
            payment_base_date = fields.Date.from_string(self.payment_base_date)
            payment_date = payment_base_date + relativedelta(
                days=self.payment_days)
        self.payment_date = payment_date

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
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('signature_process', 'Signature Process'),
            ('signed', 'Signed'),
            ('cancel', 'Cancelled'),
            ('proforma', 'Pro-forma'),
            ('posted', 'Posted')
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

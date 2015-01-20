# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class account_voucher(models.Model):
    _inherit = "account.voucher"

    payment_line_ids = fields.One2many(
        'payment.line', 'voucher_id', 'Payment Lines', readonly=True)

    payment_order_id = fields.Many2one(
        'payment.order', 'Payment Order', readonly=True, copy=False)

    @api.one
    def unlink(self):
        if self.payment_order_id:
            raise Warning(_('You can not delete a voucher that has been generated froma Payment Order, you should cancel the payment order.'))
        return super(account_voucher, self).unlink()

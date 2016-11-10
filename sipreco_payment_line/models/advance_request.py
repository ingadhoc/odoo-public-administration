# -*- coding: utf-8 -*-
from openerp import models, api


class advance_request(models.Model):
    """"""

    _inherit = 'public_budget.advance_request'

    @api.multi
    def create_voucher(self):
        voucher = super(advance_request, self).create_voucher()
        for line in self.advance_request_line_ids:
            partner = line.employee_id
            voucher.payment_line_ids.create({
                'voucher_id': voucher.id,
                'partner_id': partner.id,
                'bank_account_id': (
                    partner.bank_ids and partner.bank_ids[0].id or False),
                'amount': line.approved_amount,
            })
        return voucher

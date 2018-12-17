# -*- coding: utf-8 -*-
from odoo import models, api


class advance_request(models.Model):
    """"""

    _inherit = 'public_budget.advance_request'

    @api.multi
    def create_payment_group(self):
        payment_group = super(advance_request, self).create_payment_group()
        for line in self.advance_request_line_ids:
            partner = line.employee_id
            payment_group.line_ids.create({
                'payment_group_id': payment_group.id,
                'partner_id': partner.id,
                'bank_account_id': (
                    partner.bank_ids and partner.bank_ids[0].id or False),
                'amount': line.approved_amount,
            })
        return payment_group

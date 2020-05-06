from odoo import models, api


class AdvanceRequest(models.Model):

    _inherit = 'public_budget.advance_request'

    def create_payment_group(self):
        payment_group = super(AdvanceRequest, self).create_payment_group()
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

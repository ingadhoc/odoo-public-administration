# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
import datetime


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.multi
    def get_period_payments_domain(self, payment_group):
        """ en sipreco usamos to_signature_date en vez de payment_date
        """
        to_date = fields.Date.from_string(
            payment_group.to_signature_date) or datetime.date.today()
        common_previous_domain = [
            ('partner_id.commercial_partner_id', '=',
                payment_group.commercial_partner_id.id),
        ]
        if self.withholding_accumulated_payments == 'month':
            from_relative_delta = relativedelta(day=1)
        elif self.withholding_accumulated_payments == 'year':
            from_relative_delta = relativedelta(day=1, month=1)
        from_date = to_date + from_relative_delta
        common_previous_domain += [
            ('to_signature_date', '<=', to_date),
            ('to_signature_date', '>=', from_date),
        ]

        previous_payment_groups_domain = common_previous_domain + [
            ('state', 'not in', ['draft', 'cancel', 'confirmed']),
            ('id', '!=', payment_group.id),
        ]
        # for compatibility with public_budget we check state not in and not
        # state in posted. Just in case someone implements payments cancelled
        # on posted payment group, we remove the cancel payments (not the
        # draft ones as they are also considered by public_budget)
        previous_payments_domain = common_previous_domain + [
            ('payment_group_id.state', 'not in',
                ['draft', 'cancel', 'confirmed']),
            ('state', '!=', 'cancel'),
            ('tax_withholding_id', '=', self.id),
            ('payment_group_id.id', '!=', payment_group.id),
        ]
        return (previous_payment_groups_domain, previous_payments_domain)

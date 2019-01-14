##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
import datetime
import logging
import time

_logger = logging.getLogger(__name__)


class PurchaseSubscription(models.Model):
    _inherit = 'purchase.subscription'

    expedient_id = fields.Many2one(
        'public_budget.expedient',
        required=True,
    )

    @api.model
    def cron_account_analytic_account(self):
        remind = {}

        def fill_remind(key, domain, write_pending=False):
            base_domain = [
                ('partner_id', '!=', False),
                ('manager_id', '!=', False),
                ('manager_id.email', '!=', False),
            ]
            base_domain.extend(domain)
            accounts = self.search(base_domain, order='name asc')
            for account in accounts:
                if write_pending:
                    account.write({'state': 'pending'})
                remind_user = remind.setdefault(account.manager_id.id, {})
                remind_type = remind_user.setdefault(key, {})
                remind_type.setdefault(
                    account.partner_id, []).append(account)

        # Already expired
        fill_remind("old", [('state', 'in', ['pending'])])

        # Expires now
        fill_remind("new", [('state', 'in', ['draft', 'open']),
                            '&', ('date', '!=', False),
                            ('date', '<=', time.strftime('%Y-%m-%d')),
                            ], True)

        # Expires in less than 30 days
        fill_remind("30days", [
            ('state', 'in', ['draft', 'open']),
            ('date', '!=', False),
            ('date', '<', (fields.Datetime.now() + datetime
                           .timedelta(30)).strftime("%Y-%m-%d"))])

        # Expires in less than 60 days
        fill_remind("60days", [
            ('state', 'in', ['draft', 'open']),
            ('date', '!=', False),
            ('date', '>=', (fields.Datetime.now() + datetime
                            .timedelta(30)).strftime("%Y-%m-%d")),
            ('date', '<', (fields.Datetime.now() + datetime
                           .timedelta(60)).strftime("%Y-%m-%d"))])
        # Expires in less than 90 days
        fill_remind("90days", [
            ('state', 'in', ['draft', 'open']),
            ('date', '!=', False),
            ('date', '>=', (fields.Datetime.now() + datetime
                            .timedelta(60)).strftime("%Y-%m-%d")),
            ('date', '<', (fields.Datetime.now() + datetime
                           .timedelta(90)).strftime("%Y-%m-%d"))])
        base_url = self.env['ir.config_parameter'].get_param(
            'web.base.url')
        action_id = self.env.ref(
            'purchase_subscription.purchase_subscription_action').id
        template_id = self.env.ref(
            'purchase_subscription.'
            'purchase_account_analytic_cron_email_template').id
        for user_id, data in remind.items():
            _logger.debug("Sending reminder to uid %s", user_id)
            self.env['mail.template'].browse(template_id).with_context(
                base_url=base_url, action_id=action_id, data=data).send_mail(
                user_id, force_send=True)
        return True

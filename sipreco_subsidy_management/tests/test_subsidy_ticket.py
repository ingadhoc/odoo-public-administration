from unittest.mock import MagicMock, patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestSubsidyTicketDni(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dni_type = cls.env['l10n_latam.identification.type'].search([('name', '=', 'DNI')], limit=1)

    def _create_ticket(self, values):
        # create() reads the website user from the request
        fake_http = MagicMock()
        fake_http.request.env.user = self.env.user
        with patch('odoo.addons.sipreco_subsidy_management.models.subsidy_ticket.http', fake_http):
            return self.env['helpdesk.ticket'].create(dict(values, name='Subsidio'))

    def test_seven_digit_dni_existing_partner(self):
        partner = self.env['res.partner'].create({'name': 'Solicitante', 'vat': '5395633'})
        ticket = self._create_ticket({'dni': '5395633', 'partner_name': 'Solicitante'})
        self.assertEqual(ticket.partner_id, partner)
        self.assertEqual(partner.l10n_latam_identification_type_id, self.dni_type)
        self.assertTrue(partner.subsidy_recipient)

    def test_seven_digit_dni_new_partner(self):
        ticket = self._create_ticket({'dni': '5395634', 'partner_name': 'Solicitante nuevo'})
        self.assertEqual(ticket.partner_id.vat, '5395634')
        self.assertEqual(ticket.partner_id.l10n_latam_identification_type_id, self.dni_type)
        self.assertTrue(ticket.partner_id.subsidy_recipient)

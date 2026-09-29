from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestRemit(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Location = cls.env['public_budget.location']
        cls.location_a = Location.create({'name': 'Location A', 'expedient_management': True})
        cls.location_b = Location.create({'name': 'Location B', 'expedient_management': True})
        cls.location_c = Location.create({'name': 'Location C', 'expedient_management': True})
        cls.expedient = cls.env['public_budget.expedient'].create({
            'description': 'Test expedient',
            'pages': 1,
            'founder_id': cls.env['public_budget.expedient_founder'].create({'name': 'Founder'}).id,
            'category_id': cls.env['public_budget.expedient_category'].create({'name': 'Category'}).id,
            'first_location_id': cls.location_a.id,
        })
        cls.now = fields.Datetime.now()

    def _create_remit(self, origin, destination, minutes_ago, expedients=None):
        return self.env['public_budget.remit'].create({
            'location_id': origin.id,
            'location_dest_id': destination.id,
            'date': self.now - timedelta(minutes=minutes_ago),
            'expedient_ids': [(6, 0, (self.expedient if expedients is None else expedients).ids)],
        })

    def test_move_expedient_in_transit(self):
        self._create_remit(self.location_a, self.location_b, 60)
        with self.assertRaises(ValidationError):
            self._create_remit(self.location_a, self.location_c, 30)

    def test_move_expedient_from_other_location(self):
        self._create_remit(self.location_a, self.location_b, 60).state = 'confirmed'
        with self.assertRaises(ValidationError):
            self._create_remit(self.location_a, self.location_c, 30)

    def test_add_expedient_to_remit_older_than_last_move(self):
        """ Remito creado vacío antes del último movimiento del expediente, al que se le agrega
        el expediente cuando ya volvió a su ubicación de origen (caso tarea 76101). """
        self._create_remit(self.location_a, self.location_b, 90).state = 'confirmed'
        older_remit = self._create_remit(
            self.location_b, self.location_c, 60, expedients=self.env['public_budget.expedient'])
        self._create_remit(self.location_b, self.location_a, 45).state = 'confirmed'
        self._create_remit(self.location_a, self.location_b, 30).state = 'confirmed'
        self.assertEqual(self.expedient.current_location_id, self.location_b)
        with self.assertRaises(ValidationError):
            older_remit.expedient_ids = self.expedient

    def test_reactivate_remit_older_than_last_move(self):
        remit = self._create_remit(self.location_a, self.location_b, 60)
        remit.action_cancel()
        self._create_remit(self.location_a, self.location_c, 30).state = 'confirmed'
        with self.assertRaises(ValidationError):
            remit.action_cancel_in_transit()

    def test_move_expedient_from_current_location(self):
        self._create_remit(self.location_a, self.location_b, 60).state = 'confirmed'
        self._create_remit(self.location_b, self.location_c, 30)
        self.assertEqual(self.expedient.current_location_id, self.location_c)
        self.assertTrue(self.expedient.in_transit)

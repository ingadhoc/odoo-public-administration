from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPurchaseRequisitionComparative(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Client databases carry this historic sequence; fresh ones do not.
        if not cls.env['ir.sequence'].search_count(
                [('code', '=', 'purchase.requisition.purchase.tender')]):
            cls.env['ir.sequence'].create({
                'name': 'Purchase Tender',
                'code': 'purchase.requisition.purchase.tender',
                'prefix': 'SC',
                'padding': 5,
            })
        cls.vendor = cls.env['res.partner'].create({'name': 'Vendor'})
        cls.other_vendor = cls.env['res.partner'].create({'name': 'Other vendor'})
        cls.squeegee = cls.env['product.product'].create({
            'name': 'Squeegee', 'purchase_ok': True})
        cls.bucket = cls.env['product.product'].create({
            'name': 'Bucket', 'purchase_ok': True})
        cls.requisition = cls.env['purchase.requisition'].create({
            'line_ids': [
                (0, 0, {'product_id': cls.squeegee.id, 'name': '38 cm', 'product_qty': 4}),
                (0, 0, {'product_id': cls.squeegee.id, 'name': '25 cm', 'product_qty': 2}),
                (0, 0, {'product_id': cls.bucket.id, 'product_qty': 1}),
            ],
        })
        cls.line_38, cls.line_25, cls.line_bucket = cls.requisition.line_ids

    def _create_order(self, lines, vendor=None):
        return self.env['purchase.order'].create({
            'partner_id': (vendor or self.vendor).id,
            'requisition_id': self.requisition.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': name,
                'product_qty': qty,
                'price_unit': price,
            }) for product, name, qty, price in lines],
        })

    def _prices(self, order):
        """Unit price of each row for ``order`` as (number, price) pairs."""
        return [
            (row['number'], row['quotes'][order.id].price_unit)
            for row in self.requisition.get_comparative_rows()
        ]

    def test_matched_by_description(self):
        """The order copied the descriptions: they win over the line order."""
        order = self._create_order([
            (self.squeegee, '25 cm', 2, 200.0),
            (self.squeegee, '38 cm', 4, 100.0),
            (self.bucket, 'Bucket', 1, 50.0),
        ])
        self.assertEqual(self._prices(order), [(1, 100.0), (2, 200.0), (3, 50.0)])

    def test_matched_by_quantity(self):
        """The order kept the product name: repeated products match by quantity."""
        order = self._create_order([
            (self.squeegee, 'Squeegee', 2, 200.0),
            (self.squeegee, 'Squeegee', 4, 100.0),
            (self.bucket, 'Bucket', 1, 50.0),
        ])
        self.assertEqual(self._prices(order), [(1, 100.0), (2, 200.0), (3, 50.0)])

    def test_alternatives_add_rows(self):
        """An extra line goes under the item above it, as «N (opción 2)»."""
        order = self._create_order([
            (self.squeegee, 'Squeegee', 4, 100.0),
            (self.squeegee, 'Squeegee', 4, 90.0),
            (self.squeegee, 'Squeegee', 2, 200.0),
            (self.bucket, 'Bucket', 1, 50.0),
        ])
        other_order = self._create_order(
            [(self.squeegee, 'Squeegee', 4, 110.0)], vendor=self.other_vendor)
        self.assertEqual(
            self._prices(order),
            [(1, 100.0), ('1 (opción 2)', 90.0), (2, 200.0), (3, 50.0)])
        self.assertEqual(
            self._prices(other_order),
            [(1, 110.0), ('1 (opción 2)', 0.0), (2, 0.0), (3, 0.0)])

    def test_missing_quote_is_empty(self):
        order = self._create_order([(self.squeegee, '38 cm', 4, 100.0)])
        quotes = self.requisition._get_comparative_quotes(order)
        self.assertEqual(quotes[self.line_38.id].price_unit, 100.0)
        self.assertFalse(quotes[self.line_25.id])
        self.assertFalse(quotes[self.line_bucket.id])

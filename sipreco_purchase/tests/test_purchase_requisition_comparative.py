from odoo.tests import Form, TransactionCase, tagged


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
                'requisition_line_id': item[0].id if item else False,
            }) for product, name, qty, price, *item in lines],
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

    def test_partial_quote_matched_by_order(self):
        """The order kept the product name and the vendor quoted fewer units.

        The first item is quoted with the quantity of the second one: the
        order of the lines decides, not the quantity.
        """
        order = self._create_order([
            (self.squeegee, 'Squeegee', 2, 100.0),
            (self.squeegee, 'Squeegee', 2, 200.0),
            (self.bucket, 'Bucket', 1, 50.0),
        ])
        self.assertEqual(self._prices(order), [(1, 100.0), (2, 200.0), (3, 50.0)])

    def test_partial_quote_with_alternative(self):
        """The quoted line keeps its place although the alternative has the requested quantity."""
        order = self._create_order([
            (self.squeegee, 'Squeegee', 3, 100.0),
            (self.squeegee, 'Squeegee', 4, 90.0),
            (self.squeegee, 'Squeegee', 2, 200.0),
            (self.bucket, 'Bucket', 1, 50.0),
        ])
        self.assertEqual(
            self._prices(order),
            [(1, 100.0), ('1 (opción 2)', 90.0), (2, 200.0), (3, 50.0)])

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

    def test_repeated_description_matched_by_order(self):
        """Items with the same description are told apart by order, not by text."""
        self.requisition.line_ids = [
            (0, 0, {'product_id': self.squeegee.id, 'name': '25 cm', 'product_qty': 4})]
        order = self._create_order([
            (self.squeegee, '38 cm', 4, 100.0),
            (self.squeegee, '25 cm', 2, 200.0),
            (self.squeegee, '25 cm', 2, 190.0),
            (self.bucket, 'Bucket', 1, 50.0),
            (self.squeegee, '25 cm', 4, 300.0),
        ])
        self.assertEqual(
            self._prices(order),
            [(1, 100.0), (2, 200.0), ('2 (opción 2)', 190.0), (3, 50.0), (4, 300.0)])

    def test_order_from_requisition_links_lines(self):
        order_form = Form(self.env['purchase.order'])
        order_form.partner_id = self.vendor
        order_form.requisition_id = self.requisition
        order = order_form.save()
        self.assertEqual(order.order_line.requisition_line_id, self.requisition.line_ids)

    def test_linked_alternative_at_the_end(self):
        """A linked line goes to its item wherever it is, although the quantities point elsewhere."""
        order = self._create_order([
            (self.squeegee, 'Squeegee', 4, 100.0, self.line_38),
            (self.squeegee, 'Squeegee', 1, 200.0, self.line_25),
            (self.bucket, 'Bucket', 1, 50.0, self.line_bucket),
            (self.squeegee, 'Squeegee', 2, 90.0, self.line_38),
        ])
        self.assertEqual(
            self._prices(order),
            [(1, 100.0), ('1 (opción 2)', 90.0), (2, 200.0), (3, 50.0)])

    def test_linked_alternative_in_unlinked_order(self):
        """Linking only the alternative keeps the other lines matched as before."""
        order = self._create_order([
            (self.squeegee, 'Squeegee', 4, 100.0),
            (self.squeegee, 'Squeegee', 2, 200.0),
            (self.bucket, 'Bucket', 1, 50.0),
            (self.squeegee, 'Squeegee', 2, 90.0, self.line_38),
        ])
        self.assertEqual(
            self._prices(order),
            [(1, 100.0), ('1 (opción 2)', 90.0), (2, 200.0), (3, 50.0)])

    def test_missing_quote_is_empty(self):
        order = self._create_order([(self.squeegee, '38 cm', 4, 100.0)])
        quotes = self.requisition._get_comparative_quotes(order)
        self.assertEqual(quotes[self.line_38.id].price_unit, 100.0)
        self.assertFalse(quotes[self.line_25.id])
        self.assertFalse(quotes[self.line_bucket.id])

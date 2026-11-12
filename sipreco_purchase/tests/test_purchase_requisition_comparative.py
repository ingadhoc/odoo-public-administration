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
        cls.squeegee = cls.env['product.product'].create({
            'name': 'Squeegee', 'purchase_ok': True})
        cls.bucket = cls.env['product.product'].create({
            'name': 'Bucket', 'purchase_ok': True})
        cls.requisition = cls.env['purchase.requisition'].create({
            'line_ids': [
                (0, 0, {'product_id': cls.squeegee.id, 'name': '38 cm', 'product_qty': 4}),
                (0, 0, {'product_id': cls.squeegee.id, 'name': '25 cm', 'product_qty': 4}),
                (0, 0, {'product_id': cls.squeegee.id, 'name': '25 cm', 'product_qty': 2}),
                (0, 0, {'product_id': cls.bucket.id, 'product_qty': 1}),
            ],
        })
        cls.line_38, cls.line_25, cls.line_25_bis, cls.line_bucket = cls.requisition.line_ids

    def _create_order(self, lines):
        return self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
            'requisition_id': self.requisition.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': name,
                'product_qty': 1,
                'price_unit': price,
            }) for product, name, price in lines],
        })

    def test_same_product_matched_by_description_and_order(self):
        order = self._create_order([
            (self.bucket, 'Bucket', 50.0),
            (self.squeegee, '25 cm', 200.0),
            (self.squeegee, '38 cm', 100.0),
            (self.squeegee, '25 cm', 300.0),
        ])
        prices = [
            line.get_comparative_order_line(order).price_unit
            for line in self.requisition.line_ids
        ]
        # The bucket has no description on the requisition: matched by product.
        self.assertEqual(prices, [100.0, 200.0, 300.0, 50.0])

    def test_missing_quote_returns_empty(self):
        order = self._create_order([(self.squeegee, '38 cm', 100.0)])
        self.assertEqual(self.line_38.get_comparative_order_line(order).price_unit, 100.0)
        self.assertFalse(self.line_25.get_comparative_order_line(order))
        self.assertFalse(self.line_25_bis.get_comparative_order_line(order))
        self.assertFalse(self.line_bucket.get_comparative_order_line(order))

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPreaward(TransactionCase):

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
                (0, 0, {'product_id': cls.squeegee.id, 'product_qty': 4}),
                (0, 0, {'product_id': cls.bucket.id, 'product_qty': 1}),
            ],
        })
        cls.line_squeegee, cls.line_bucket = cls.requisition.line_ids
        cls.first = cls._create_order(cls.vendor, [(cls.squeegee, 4, 100.0), (cls.bucket, 1, 50.0)])
        cls.second = cls._create_order(cls.other_vendor, [(cls.squeegee, 4, 120.0), (cls.bucket, 1, 30.0)])

    @classmethod
    def _create_order(cls, vendor, lines):
        return cls.env['purchase.order'].create({
            'partner_id': vendor.id,
            'requisition_id': cls.requisition.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': product.name,
                'product_qty': qty,
                'price_unit': price,
            }) for product, qty, price in lines],
        })

    def _preaward(self, order, product):
        line = order.order_line.filtered(lambda x: x.product_id == product)
        line.preaward = True
        return line

    def test_clear_unawarded_quantities(self):
        """Only the lines left out of the preaward are zeroed."""
        awarded = self._preaward(self.first, self.squeegee) | self._preaward(self.second, self.bucket)
        self.requisition.action_clear_unawarded_quantities()
        self.assertEqual(awarded.mapped('product_qty'), [4.0, 1.0])
        left_out = (self.first | self.second).order_line - awarded
        self.assertEqual(left_out.mapped('product_qty'), [0.0, 0.0])

    def test_clear_without_lines_raises(self):
        """Everything preawarded: there is nothing to zero and it says so."""
        (self.first | self.second).order_line.preaward = True
        with self.assertRaises(UserError):
            self.requisition.action_clear_unawarded_quantities()

    def test_preaward_detail_groups_by_vendor(self):
        """Each vendor brings its preawarded lines and their amount."""
        self._preaward(self.first, self.squeegee)
        self._preaward(self.second, self.bucket)
        detail = self.requisition.get_preaward_detail()
        self.assertEqual([group['purchase'] for group in detail], [self.first, self.second])
        self.assertEqual([group['amount'] for group in detail], [400.0, 30.0])

    def test_preaward_detail_skips_vendors_without_lines(self):
        """A vendor with nothing preawarded is not in the detail."""
        self._preaward(self.first, self.squeegee)
        detail = self.requisition.get_preaward_detail()
        self.assertEqual([group['purchase'] for group in detail], [self.first])

    def test_preaward_items_follow_the_comparison(self):
        """One entry per preawarded line, in the order of the comparison."""
        self._preaward(self.first, self.squeegee)
        self._preaward(self.second, self.bucket)
        items = self.requisition.get_preaward_items()
        self.assertEqual([item["line"] for item in items],
                         [self.line_squeegee, self.line_bucket])
        self.assertEqual([item["quote"].partner_id for item in items],
                         [self.vendor, self.other_vendor])

    def test_print_stamps_once(self):
        """The sheet keeps the first stamp: reprinting does not move it."""
        self.requisition.print_preaward_report()
        stamp = (self.requisition.preaward_user_id, self.requisition.preaward_date)
        self.assertEqual(stamp[0], self.env.user)
        self.requisition.print_preaward_report()
        self.assertEqual(
            (self.requisition.preaward_user_id, self.requisition.preaward_date), stamp)

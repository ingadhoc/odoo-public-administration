##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(
            self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        result = super()._get_stock_move_values(product_id, product_qty,
                                                product_uom, location_id, name, origin, company_id, values)
        stock_request_id = values.get('stock_request_id', False)
        if stock_request_id:
            stock_request = self.env['stock.request'].browse(stock_request_id)
            stock_request.rule_id = self.id
            result['name'] = stock_request.description
        return result

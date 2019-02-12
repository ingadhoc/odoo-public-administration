##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    stock_request_selectable = fields.Boolean(
        'Applicable on Stock Requests',
    )

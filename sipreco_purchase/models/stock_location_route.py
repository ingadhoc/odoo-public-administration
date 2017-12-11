# -*- coding: utf-8 -*-
from openerp import models, fields
# from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    stock_request_selectable = fields.Boolean(
        'Applicable on Stock Requests',
    )

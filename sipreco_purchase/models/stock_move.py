# -*- coding: utf-8 -*-
from openerp import models
# from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    # lo movimos a procurement.order
    # requisition_id = fields.Many2one(
    #     'purchase.requisition',
    #     'Purchase Requisition',
    #     readonly=True,
    # )

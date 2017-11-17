# -*- coding: utf-8 -*-
from openerp import models, fields
# from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    requisition_id = fields.Many2one(
        'purchase.requisition',
        'Purchase Requisition',
        readonly=True,
    )

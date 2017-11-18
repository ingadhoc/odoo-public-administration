# -*- coding: utf-8 -*-
from openerp import models, fields
# from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    move_ids = fields.One2many(
        'procurement.order',
        'manual_requisition_id',
        'Procurements',
        # 'stock.move',
        # 'requisition_id',
        # 'Supply Requirements',
    )

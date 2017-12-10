# -*- coding: utf-8 -*-
from openerp import models, fields
import openerp.addons.decimal_precision as dp
# from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    name = fields.Text(
        string='Description',
    )
    price_unit = fields.Float(
        string='Unit Price',
        digits=dp.get_precision('Product Price'),
    )

# -*- coding: utf-8 -*-
from openerp import models
# from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # ahora lo hacemos en requests, se podria borrar
    # partner_id = fields.Many2one(
    #     default=lambda x: x.env.user.partner_id.id
    # )

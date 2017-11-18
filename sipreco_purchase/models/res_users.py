# -*- coding: utf-8 -*-
from openerp import models, fields
# from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    picking_type_ids = fields.Many2many(
        'stock.picking.type',
        'stock_picking_type_users_rel',
        'user_id',
        'picking_type_id',
        'Restricted Picking Types',
    )

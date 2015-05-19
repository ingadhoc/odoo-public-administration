# -*- coding: utf-8 -*-
from openerp import fields, models, _, api
from openerp.exceptions import Warning
import logging
import openerp.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)


class account_check(models.Model):

    _inherit = ['account.check']

    delivered = fields.Boolean(
        'Delivered?'
        )

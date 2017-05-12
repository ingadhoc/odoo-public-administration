# -*- coding: utf-8 -*-
from openerp import models
import logging
_logger = logging.getLogger(__name__)


class account_move_line(models.Model):

    _inherit = 'account.move.line'

    # TODO implementar esto
    # voucher_line_ids = fields.One2many(
    #     'account.voucher.line',
    #     'move_line_id',
    #     'Voucher Lines'
    # )
    # TODO agregar y ver si usamos
    # to_pay_amount = fields.Monetary(
    #     related='invoice_id.to_pay_amount',
    # )

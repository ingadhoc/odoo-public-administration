# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
import logging
_logger = logging.getLogger(__name__)


class budget(models.Model):

    _inherit = 'public_budget.budget'

    receiptbook_id = fields.Many2one(
        'account.voucher.receiptbook',
        'ReceiptBook',
        required=True,
        states={'draft': [('readonly', False)]},
        domain="[('type', '=', 'payment'), ('company_id', '=', company_id)]",
        )

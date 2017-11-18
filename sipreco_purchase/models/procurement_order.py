# -*- coding: utf-8 -*-
from openerp import models, fields
# from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    # odoo ya tiene un requisition_id que es cuando se correr el "buy", en este
    # caso es un link independiente a eso lo que queremos, un link manual y sin
    # funcionalidad prácticamente
    manual_requisition_id = fields.Many2one(
        'purchase.requisition',
        'Purchase Requisition',
        readonly=True,
    )
    partner_id = fields.Many2one(
        related='group_id.partner_id',
        readonly=True,
    )

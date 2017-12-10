# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    name = fields.Char(
        # cambiamos string
        'Reference',
    )
    manual_procurement_ids = fields.One2many(
        'procurement.order',
        'manual_requisition_id',
        'Procurements',
        # 'stock.move',
        # 'requisition_id',
        # 'Supply Requirements',
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        'Tramite Administrativo',
    )
    type_id = fields.Many2one(
        'public_budget.transaction_type',
        string='Type',
        # readonly=True,
        # states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id)]",
    )

    @api.multi
    def tender_cancel(self):
        self.mapped('manual_procurement_ids').button_cancel_remaining()
        return super(PurchaseRequisition, self).tender_cancel()

    @api.multi
    def tender_open(self):
        for rec in self:
            if not rec.purchase_ids:
                raise ValidationError(_(
                    'No se puede cerrar la licitación si no se solicitaron '
                    'presupuestos'))
        return super(PurchaseRequisition, self).tender_open()

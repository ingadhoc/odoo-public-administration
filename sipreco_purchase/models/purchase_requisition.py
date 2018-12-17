# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import odoo.addons.decimal_precision as dp
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
        ondelete='restrict',
    )
    type_id = fields.Many2one(
        'public_budget.transaction_type',
        string='Type',
        # readonly=True,
        # states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id)]",
        track_visibility='onchange',
    )

    inspected = fields.Boolean(
        'Inspected?'
    )

    amount_total = fields.Float(
        digits=dp.get_precision('Product Price'),
        compute='_compute_amount_total',
    )

    date = fields.Date(
        'Start Date',
        readonly=True,
    )
    user_inspected = fields.Char(
        track_visibility='onchange',
    )
    user_confirmed = fields.Char(
        track_visibility='onchange',
    )

    @api.depends('line_ids')
    def _compute_amount_total(self):
        for rec in self.filtered('line_ids'):
            rec.amount_total = sum([x.subtotal for x in rec.line_ids])

    @api.multi
    def to_inspected(self):
        if not self.type_id:
            raise UserError(_('Antes de revisar debe tener establecido un'
                              '"Tipo"'))
        self.inspected = True
        self.user_inspected = self.env.user.name

    @api.multi
    def to_draft(self):
        if self.state == 'draft' and self.inspected:
            self.inspected = False
        elif self.state == 'in_progress':
            self.with_context(cancel_procurement=False).tender_cancel()
            self.tender_reset()

    @api.multi
    def tender_cancel(self):
        if self._context.get('cancel_procurement', True):
            self.mapped('manual_procurement_ids').button_cancel_remaining()
        self.inspected = False
        self.user_inspected = False
        self.user_confirmed = False
        return super(PurchaseRequisition, self).tender_cancel()

    @api.multi
    def tender_open(self):
        for rec in self:
            if not rec.purchase_ids:
                raise ValidationError(_(
                    'No se puede cerrar la licitación si no se solicitaron '
                    'presupuestos'))
        return super(PurchaseRequisition, self).tender_open()

    @api.model
    def create(self, vals):
        vals['date'] = fields.Date.today()
        return super(PurchaseRequisition, self).create(vals)

    @api.multi
    def tender_in_progress(self):
        self.user_confirmed = self.env.user.name
        super(PurchaseRequisition, self).tender_in_progress()

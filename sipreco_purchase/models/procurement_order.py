# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError
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
        'Solicitud de Compra',
        # 'Purchase Requisition',
        readonly=True,
    )
    partner_id = fields.Many2one(
        related='group_id.partner_id',
        readonly=True,
    )
    price_unit = fields.Float(
        string='Unit Price',
        readonly=True,
        states={'confirmed': [('readonly', False)]},
        digits=dp.get_precision('Product Price'),
    )
    # hacemos readonly para no confundir porque se generó el picking
    name = fields.Text(
        readonly=True,
        states={'confirmed': [('readonly', False)]},
    )
    requirement_id = fields.Many2one(
        related='procurement_request_id.partner_id',
        readonly=True,
        string='Requirent'
    )

    @api.model
    def create(self, vals):
        # controlamos que haya definido cantidad
        if not vals.get('product_qty'):
            raise ValidationError(_(
                'You can not create a request without quantity!'))
        return super(ProcurementOrder, self).create(vals)

    @api.multi
    def onchange_product_id(self, product_id):
        res = super(ProcurementOrder, self).onchange_product_id(product_id)
        if 'value' not in res:
            res['value'] = {}
        product = self.env['product.product'].browse(
            product_id)
        res['value']['name'] = product.partner_ref
        res['value']['price_unit'] = product.standard_price
        return res

    @api.multi
    def run(self, autocommit=False):
        """
        Después de ejecutar procurement intentar reservar automáticamente
        los pikcings
        """
        res = super(ProcurementOrder, self).run(autocommit=autocommit)
        # hacemos jit en los pickings vinculados
        if self.mapped('group_id').ids:
            reassign_pickinkgs = self.env['stock.picking'].search([
                ('group_id', 'in', self.mapped('group_id').ids),
                ('state', 'in', [
                    'confirmed', 'partially_available', 'waiting'])])
            if reassign_pickinkgs:
                reassign_pickinkgs.do_unreserve()
                reassign_pickinkgs.action_assign()
        return res

##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError


class StockRequest(models.Model):
    _inherit = 'stock.request'

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
        related='procurement_group_id.partner_id',
        readonly=True,
    )
    price_unit = fields.Float(
        string='Unit Price',
        readonly=True,
        states={'draft': [('readonly', False)]},
        digits=dp.get_precision('Product Price'),
    )
    # hacemos readonly para no confundir porque se generó el picking
    description = fields.Text(
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    requirement_id = fields.Many2one(
        related='order_id.partner_id',
        readonly=True,
    )
    rule_id = fields.Many2one(
        'procurement.rule',
        track_visibility='onchange',
        help="Chosen rule for the procurement resolution."
        " Usually chosen by the system but can be manually set by the"
        " procurement manager to force an unusual behavior.",
    )

    activity_date_deadline = fields.Date(
        related_sudo=True,
        compute_sudo=True,
    )

    @api.model
    def create(self, vals):
        # controlamos que haya definido cantidad
        if not vals.get('product_uom_qty'):
            raise ValidationError(_(
                'You can not create a request without quantity!'))
        return super(StockRequest, self).create(vals)

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(StockRequest, self).onchange_product_id()
        self.update({
            'description': self.product_id.partner_ref,
            'price_unit': self.product_id.standard_price,
        })
        return res

    @api.multi
    def _action_launch_procurement_rule(self):
        """
        Después de ejecutar procurement intentar reservar automáticamente
        los pikcings
        """
        res = super(StockRequest, self)._action_launch_procurement_rule()
        # hacemos jit en los pickings vinculados
        if self.mapped('procurement_group_id').ids:
            reassign_pickinkgs = self.env['stock.picking'].search([
                ('group_id', 'in', self.mapped(
                    'procurement_group_id').ids),
                ('state', 'in', [
                    'confirmed', 'partially_available', 'waiting'])])
            if reassign_pickinkgs:
                reassign_pickinkgs.do_unreserve()
                reassign_pickinkgs.action_assign()
        return res

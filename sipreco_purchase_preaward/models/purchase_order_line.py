##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    preaward = fields.Boolean(
        'Preadjudicada',
        copy=False,
        help='Línea elegida en la preadjudicación de la solicitud de compra.',
    )

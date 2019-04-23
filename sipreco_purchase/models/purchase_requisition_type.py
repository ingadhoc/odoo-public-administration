##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class PurchaseRequisitionType(models.Model):
    _inherit = "purchase.requisition.type"

    price_unit_copy = fields.Selection(
        [('copy', 'Use price of agreement'),
         ('none', 'Set price manually')],
        string='Price Unit',
        required=True,
        default='none',
    )

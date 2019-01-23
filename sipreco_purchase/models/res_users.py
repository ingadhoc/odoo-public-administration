##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    picking_type_ids = fields.Many2many(
        'stock.picking.type',
        'stock_picking_type_users_rel',
        'user_id',
        'picking_type_id',
        'Restricted Picking Types',
    )

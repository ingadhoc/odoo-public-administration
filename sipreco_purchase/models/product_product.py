##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    standard_price = fields.Float(
        groups='base.group_user,\
        sipreco_purchase.group_portal_requester')



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_piking_type_ids = fields.Many2many(comodel_name='stock.picking.type', string='Tipos de Operaciones' , compute="_compute_stock_picking_types",store=True)


    @api.depends('route_ids')
    def _compute_stock_picking_types(self):
        for rec in self:
            stock_piking_type_ids = rec.route_ids.mapped('rule_ids.picking_type_id') if rec.route_ids and rec.route_ids.rule_ids  else False
            if stock_piking_type_ids:
                rec.stock_piking_type_ids = stock_piking_type_ids.ids

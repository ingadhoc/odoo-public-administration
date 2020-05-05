##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    partner_id = fields.Many2one(
        'res.partner',
        'Requirente',
        required=True,
        default=lambda self: self.env.user.partner_id
    )
    description = fields.Text(
        'Motivacion',
        required=True,
    )
    activity_date_deadline = fields.Date(
        related_sudo=True,
        compute_sudo=True,
    )

    @api.onchange('company_id')
    def change_company_id(self):
        self.warehouse_id = self.env['stock.warehouse'].search(
            [('company_id', '=', self.company_id.id)], limit=1)

    @api.onchange('partner_id', 'warehouse_id')
    def onchange_warehouse_id(self):
        # clientes esta seteada en el partner
        super().onchange_warehouse_id()
        self.location_id = self.partner_id.property_stock_customer
        # # use customer location by default instead of stock location
        # self.location_id = self.warehouse_id.wh_output_stock_loc_id

    @api.model
    def create(self, vals):
        # mandamos el partner en el group ya que es este el que va hasta el
        # # picking
        rec = super().create(vals)
        if rec.procurement_group_id:
            rec.procurement_group_id.partner_id = rec.partner_id
        return rec

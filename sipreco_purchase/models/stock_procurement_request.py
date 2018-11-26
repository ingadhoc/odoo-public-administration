# -*- coding: utf-8 -*-
from openerp import models, fields, api
# from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class StockProcurementRequest(models.Model):
    _inherit = 'stock.procurement.request'

    partner_id = fields.Many2one(
        'res.partner',
        'Requirent',
        required=True,
        default=lambda self: self.env.user.partner_id
    )
    name = fields.Char(
        default='/',
    )
    route_id = fields.Many2one(
        'stock.location.route',
        compute='_compute_route',
        inverse='_inverse_route',
        string='Unidad de Compra',
        # TODO este domain podria ir en el modulo de requests
        domain=[('stock_request_selectable', '=', True)],
    )
    description = fields.Text(
        'Motivacion',
        required=True,
    )

    @api.multi
    def _inverse_route(self):
        for rec in self:
            rec.route_ids = [(6, False, [rec.route_id.id])]

    @api.multi
    @api.depends('route_ids')
    def _compute_route(self):
        for rec in self:
            rec.route_id = rec.route_ids and rec.route_ids[0] or False

    @api.onchange('company_id')
    def change_company_id(self):
        self.warehouse_id = self.env['stock.warehouse'].search(
            [('company_id', '=', self.company_id.id)], limit=1)

    @api.onchange('partner_id', 'warehouse_id')
    def change_warehouse_id(self):
        # clientes esta seteada en el partner
        self.location_id = self.partner_id.property_stock_customer
        # # use customer location by default instead of stock location
        # self.location_id = self.warehouse_id.wh_output_stock_loc_id

    @api.model
    def create(self, vals):
        # mandamos el partner en el group ya que es este el que va hasta el
        # picking
        if not vals.get('group_id'):
            # como lo hicimos readonly no esta viniendo en vals, si no viene
            # sacamos de defaults que es el que se va a asignar
            partner_id = vals.get(
                'partner_id',
                self.default_get(['partner_id']).get('partner_id'))
            group = self.group_id.create(
                {'partner_id': partner_id})
            vals['group_id'] = group.id

        if vals.get('name', '/') == '/':
            vals['name'] = self.env[
                'ir.sequence'].next_by_code('stock.procurement.request')
        return super(StockProcurementRequest, self).create(vals)

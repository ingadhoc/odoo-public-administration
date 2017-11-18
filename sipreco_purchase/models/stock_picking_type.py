# -*- coding: utf-8 -*-
from openerp import models, fields, api
# from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    # count_pending_moves = fields.Integer(
    # compute='_compute_moves_count',
    count_pending_procurements = fields.Integer(
        compute='_compute_procurements_count',
    )

    @api.multi
    def _compute_procurements_count(self):
        # reads = self.env['stock.move'].read_group(
        #     [('state', 'in', ['waiting', 'confirmed', 'assigned'])],
        #     ['picking_type_id'], ['picking_type_id'])
        # for read in reads:
        #   self.browse(read['picking_type_id'][0]).count_pending_moves = read[
        #         'picking_type_id_count']
        for rec in self:
            rec.count_pending_procurements = self.env[
                'procurement.order'].search_count([
                    ('state', 'not in', ['done', 'cancel']),
                    ('rule_id.picking_type_id', '=', rec.id)])

    @api.multi
    def action_type_procurement_orders(self):
        self.ensure_one()
        action = self.env.ref('procurement.procurement_action')
        if not action:
            return False

        res = action.read()[0]

        res['domain'] = [('rule_id.picking_type_id', '=', self.id)]
        res['context'] = {'search_default_pending': 1}
        return res

# -*- coding: utf-8 -*-
from openerp import models, fields, api
# from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    count_pending_moves = fields.Integer(
        compute='_compute_moves_count',
    )

    @api.multi
    def _compute_moves_count(self):
        reads = self.env['stock.move'].read_group(
            [('state', 'in', ['waiting', 'confirmed', 'assigned'])],
            ['picking_type_id'], ['picking_type_id'])
        for read in reads:
            self.browse(read['picking_type_id'][0]).count_pending_moves = read[
                'picking_type_id_count']

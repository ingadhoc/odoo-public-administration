##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
# ##############################################################################
from odoo import models, fields, api


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    # count_pending_moves = fields.Integer(
    # compute='_compute_moves_count',
    count_pending_requests = fields.Integer(
        compute='_compute_requests_count',
    )
    user_ids = fields.Many2many(
        'res.users',
        'stock_picking_type_users_rel',
        'picking_type_id',
        'user_id',
        string='Users',
        copy=False
    )

    def _compute_requests_count(self):
        # reads = self.env['stock.move'].read_group(
        #     [('state', 'in', ['waiting', 'confirmed', 'assigned'])],
        #     ['picking_type_id'], ['picking_type_id'])
        # for read in reads:
        #   self.browse(read['picking_type_id'][0]).count_pending_moves = read[
        #         'picking_type_id_count']
        for rec in self:
            rec.count_pending_requests = self.env[
                'stock.request'].search_count([
                    ('state', 'not in', ['done', 'cancel']),
                    ('rule_id.picking_type_id', '=', rec.id)])

    def action_type_stock_request(self):
        self.ensure_one()
        action = self.env.ref('stock_request.action_stock_request_form')
        if not action:
            return False
        res = action.read()[0]
        res['domain'] = [('rule_id.picking_type_id', '=', self.id)]
        res['context'] = {'search_default_pending': 1}
        return res

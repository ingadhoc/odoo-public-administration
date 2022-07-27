##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
# ##############################################################################
from odoo import models, fields

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

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
        for rec in self:
            rec.count_pending_requests = self.env[
                'stock.request'].search_count([
                    ('state', 'not in', ['done', 'cancel']),
                    ('rule_id.picking_type_id', '=', rec.id)])

    def action_type_stock_request(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('stock_request.action_stock_request_form')
        if not action:
            return False
        action['domain'] = [('rule_id.picking_type_id', '=', self.id)]
        action['context'] = {'search_default_pending': 1}
        return action

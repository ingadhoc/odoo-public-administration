# -*- coding: utf-8 -*-
from openerp import models, api


class res_partner(models.Model):
    """"""

    _inherit = 'res.partner'

    @api.multi
    def get_debt_amount(self, advance_return_type):
        self.ensure_one()
        requested_amount = sum(
            self.env['public_budget.advance_request_line'].search([
                ('employee_id', '=', self.id),
                ('advance_request_id.state', 'not in', ['draft', 'cancel']),
                ('advance_request_id.type_id', '=', advance_return_type.id),
            ]).mapped('approved_amount'))
        returned_amount = sum(
            self.env['public_budget.advance_return_line'].search([
                ('employee_id', '=', self.id),
                ('advance_return_id.state', 'not in', ['draft', 'cancel']),
                ('advance_return_id.type_id', '=', advance_return_type.id),
            ]).mapped('returned_amount'))
        return requested_amount - returned_amount

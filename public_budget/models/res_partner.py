# -*- coding: utf-8 -*-
from openerp import models, api, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    advance_request_debt = fields.Monetary(
        compute='get_advance_request_debt',
    )

    @api.multi
    def get_advance_request_debt(self):
        advance_return_type = self.env[
            'public_budget.advance_request_type'].browse(self._context.get(
                'advance_return_type_id', False))
        for rec in self:
            rec.advance_request_debt = rec.get_debt_amount(
                advance_return_type)

    @api.multi
    def get_debt_amount(self, advance_return_type=False, to_date=False):
        self.ensure_one()
        requested_domain = [
            ('employee_id', '=', self.id),
            ('advance_request_id.state', 'not in', ['draft', 'cancel']),
        ]
        returned_domain = [
            ('employee_id', '=', self.id),
            ('advance_return_id.state', 'not in', ['draft', 'cancel']),
        ]

        if advance_return_type:
            requested_domain.append(
                ('advance_request_id.type_id', '=', advance_return_type.id))
            returned_domain.append(
                ('advance_return_id.type_id', '=', advance_return_type.id))

        if to_date:
            requested_domain.append(
                ('advance_request_id.approval_date', '<=', to_date))
            returned_domain.append(
                ('advance_return_id.confirmation_date', '<=', to_date))

        requested_amount = sum(
            self.env['public_budget.advance_request_line'].search(
                requested_domain).mapped('approved_amount'))
        returned_amount = sum(
            self.env['public_budget.advance_return_line'].search(
                returned_domain).mapped('returned_amount'))
        return requested_amount - returned_amount

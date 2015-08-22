# -*- coding: utf-8 -*-
from openerp import models, api, fields


class definitive_line(models.Model):

    _inherit = 'public_budget.definitive_line'

    # definitive_partner_type = fields.Selection(
    definitive_partner_type = fields.Char(
        related='transaction_id.type_id.definitive_partner_type'
        # compute='_get_definitive_partner_type',
        )

    @api.one
    def _get_definitive_partner_type(self):
        print '222222222222'
        self.definitive_partner_type = (
            self.transaction_id.type_id.definitive_partner_type)
        return {'domain': {
            'supplier_id': [('subsidy_recipient', '=', True)]}}

    @api.onchange('definitive_partner_type')
    def change_definitive_partner_type(self):
        print '111111111111'
        if self.definitive_partner_type == 'subsidy_recipient':
            return {'domain': {
                'supplier_id': [('subsidy_recipient', '=', True)]}}

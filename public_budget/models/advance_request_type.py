# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class advance_request_type(models.Model):
    """"""

    _name = 'public_budget.advance_request_type'
    _description = 'Advance Request Type'

    name = fields.Char(
        'Name',
        required=True,
        )
    general_return_partner_id = fields.Many2one(
        'res.partner',
        string='General Return Partner',
        required=True
        )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        domain="[('type', '=', 'other'), ('company_id', '=', company_id)]",
        # ahora no queremos que sea payable porque no queremos que se lleve
        # a la deuda del partner generico, queremos que para que se lleve haga
        # falta hacer una devolucion
        # domain="[('type', '=', 'payable'), ('company_id', '=', company_id)]",
        required=True,
        )
    return_journal_id = fields.Many2one(
        'account.journal',
        string='Return Journal',
        domain="[('company_id', '=', company_id)]",
        required=True,
        )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id,
        )

    @api.one
    @api.constrains('type_id', 'company_id', 'return_journal_id')
    def check_company(self):
        if self.account_id.company_id != self.company_id:
            raise Warning(_(
                'Company must be the same as Account Company!'))
        if self.return_journal_id.company_id != self.company_id:
            raise Warning(_(
                'Company must be the same as Journal Company!'))

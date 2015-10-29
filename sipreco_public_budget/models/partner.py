# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class partner(models.Model):
    """"""

    _inherit = 'res.partner'

    subsidy_recipient = fields.Boolean(
        'Subsidy Recipient',
        )
    # Make some fields require
    responsability_id = fields.Many2one(
        required=True,
        )
    document_type_id = fields.Many2one(
        required=True,
        )
    document_number = fields.Char(
        required=True,
        )

    @api.one
    @api.constrains('subsidy_recipient', 'document_number')
    def check_unique_document_number(self):
        if self.subsidy_recipient and self.document_number:
            same_document_partners = self.search([
                ('document_number', '=', self.document_number),
                ('subsidy_recipient', '=', True),
                ('id', '!=', self.id),
                ])
            if same_document_partners:
                raise Warning(_(
                    'El número de documento debe ser único por receptor de '
                    'subsidio!\n'
                    '* ids de receptores: %s') % same_document_partners.ids)

    @api.multi
    def mark_as_reconciled(self):
        # run with sudo because it gives error if you dont have rights to write
        # on partner
        return super(partner, self.sudo()).mark_as_reconciled()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

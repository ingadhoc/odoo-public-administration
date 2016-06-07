# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class partner(models.Model):
    """"""

    _inherit = 'res.partner'

    subsidy_recipient = fields.Boolean(
        'Subsidy Recipient',
        )
    # Make some fields require
    # we make it required in the view so we dont have error in tests
    # and also because it is more correct, this fields should be required
    # only for a certain group of partners (perhups employees, suppliers, etc)
    # responsability_id = fields.Many2one(
    #     required=True,
    #     )
    # document_type_id = fields.Many2one(
    #     required=True,
    #     )
    # document_number = fields.Char(
    #     required=True,
    #     )

    @api.one
    @api.constrains('subsidy_recipient', 'document_number')
    def check_unique_document_number_subsidy_recipient(self):
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
                    '* Receptor existente: %s') % same_document_partners.name)

    @api.one
    @api.constrains('employee', 'document_number')
    def check_unique_document_number_employee(self):
        if self.employee and self.document_number:
            same_document_partners = self.search([
                ('document_number', '=', self.document_number),
                ('employee', '=', True),
                ('id', '!=', self.id),
                ])
            if same_document_partners:
                raise Warning(_(
                    'El número de documento debe ser único por empleado!\n'
                    '* Empleado existente: %s') % same_document_partners.name)

    @api.multi
    def mark_as_reconciled(self):
        # run with sudo because it gives error if you dont have rights to write
        # on partner
        return super(partner, self.sudo()).mark_as_reconciled()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

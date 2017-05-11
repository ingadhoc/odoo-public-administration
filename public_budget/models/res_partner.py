# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = 'res.partner'

    advance_request_debt = fields.Monetary(
        compute='get_advance_request_debt',
    )
    # TODO ver si en v10 convertimos esto a un document id del partner
    numero_legajo = fields.Char(
        'Numero de Legajo',
    )
    subsidy_recipient = fields.Boolean(
        'Subsidy Recipient',
    )

    @api.one
    @api.constrains('subsidy_recipient', 'main_id_number')
    def check_unique_document_number_subsidy_recipient(self):
        if self.subsidy_recipient and self.document_number:
            same_document_partners = self.search([
                ('main_id_number', '=', self.main_id_number),
                ('subsidy_recipient', '=', True),
                ('id', '!=', self.id),
            ])
            if same_document_partners:
                raise ValidationError(_(
                    'El número de documento debe ser único por receptor de '
                    'subsidio!\n'
                    '* Receptor existente: %s') % same_document_partners.name)

    @api.one
    @api.constrains('employee', 'main_id_number')
    def check_unique_document_number_employee(self):
        if self.employee and self.document_number:
            same_document_partners = self.search([
                ('main_id_number', '=', self.main_id_number),
                ('employee', '=', True),
                ('id', '!=', self.id),
            ])
            if same_document_partners:
                raise ValidationError(_(
                    'El número de documento debe ser único por empleado!\n'
                    '* Empleado existente: %s') % same_document_partners.name)

    @api.multi
    def mark_as_reconciled(self):
        # run with sudo because it gives error if you dont have rights to write
        # on partner
        return super(ResPartner, self.sudo()).mark_as_reconciled()

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

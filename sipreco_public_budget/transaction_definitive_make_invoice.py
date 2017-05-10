# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class public_budget_definitive_make_invoice(models.TransientModel):
    _inherit = "public_budget.definitive.make.invoice"
    _name = "public_budget.definitive.make.invoice"

    point_of_sale = fields.Integer(
        'Point Of Sale'
        )
    invoice_number = fields.Integer(
        'Invoice Number',
        )
    use_documents = fields.Boolean(
        related='journal_id.use_documents',
        readonly=True
    )
    supplier_invoice_number = fields.Char(
        required=False,
    )

    @api.onchange('point_of_sale', 'invoice_number', 'use_documents')
    def _check_invoice_number(self):
        if self.use_documents and (self.point_of_sale or self.invoice_number):
            if self.point_of_sale > 9999:
                self.point_of_sale = 0
                raise ValidationError(_('Point of Sale must be lower than 9999'))
            if self.invoice_number > 99999999:
                self.invoice_number = 0
                raise ValidationError(_('Invoice number must be lower than 99999999'))
            supplier_invoice_number = '%%0%ii' % 4 % self.point_of_sale
            supplier_invoice_number += '-%%0%ii' % 8 % self.invoice_number
            self.supplier_invoice_number = supplier_invoice_number
        else:
            self.supplier_invoice_number = False

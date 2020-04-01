from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class PublicBudgetDefinitiveMakeInvoiceDetail(models.TransientModel):
    _name = "public_budget.definitive.make.invoice.detail"

    definitive_make_invoice_id = fields.Many2one(
        'public_budget.definitive.make.invoice',
        'Def Make Invoice',
    )
    definitive_line_id = fields.Many2one(
        'public_budget.definitive_line',
        'Def Make Invoice',
        readonly=True,
    )
    residual_amount = fields.Monetary(
        related='definitive_line_id.residual_amount',
    )
    to_invoice_amount = fields.Monetary(
        'Amount',
    )
    full_imputation = fields.Boolean(
        'Full Imputation?',
    )
    currency_id = fields.Many2one(
        related='definitive_line_id.currency_id',
    )

    @api.onchange('full_imputation')
    def change_full_imputation(self):
        self.to_invoice_amount = self.definitive_line_id.residual_amount

    @api.constrains(
        'to_invoice_amount'
    )
    def _check_amounts(self):
        for rec in self.filtered(
            lambda x: float_compare(
                x.residual_amount, x.to_invoice_amount,
                precision_rounding=x.currency_id.rounding) < 0):
            raise ValidationError(
                _("To Invoice Amount can't be greater than Residual Amount"))

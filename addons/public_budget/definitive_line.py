# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class definitive_line(models.Model):
    """Definitive Line"""

    _name = 'public_budget.definitive_line'
    _description = 'Definitive Line'

    issue_date = fields.Date(
        string='Issue Date',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today
        )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        context={'default_supplier': True},
        domain=[('supplier', '=', True)]
        )
    amount = fields.Float(
        string='Amount',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
        )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        readonly=True
        )
    full_imputation = fields.Boolean(
        string='Full Imputation',
        compute='_get_full_imputation'
        )
    residual_amount = fields.Float(
        string='Residual Amount',
        compute='_get_amounts'
        )
    to_pay_amount = fields.Float(
        string='To Pay Amount',
        compute='_get_amounts'
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        compute='_get_amounts'
        )
    invoiced_amount = fields.Float(
        string='Invoiced Amount',
        compute='_get_amounts'
        )
    to_invoice_amount = fields.Float(
        string='To Invoice'
        )
    transaction_id = fields.Many2one(
        comodel_name='public_budget.transaction',
        string='Transaction',
        readonly=True,
        store=True,
        related='preventive_line_id.transaction_id'
        )
    budget_id = fields.Many2one(
        comodel_name='public_budget.budget',
        string='Budget',
        readonly=True,
        store=True,
        related='preventive_line_id.budget_id'
        )
    budget_position_id = fields.Many2one(
        comodel_name='public_budget.budget_position',
        string='Budget Position',
        readonly=True,
        store=True,
        related='preventive_line_id.budget_position_id'
        )
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('invoiced', 'Invoiced')],
        string='State',
        states={'draft': [('readonly', False)]},
        default='draft',
        compute='_get_state'
        )
    preventive_line_id = fields.Many2one(
        'public_budget.preventive_line',
        ondelete='cascade',
        string='Preventive Line',
        required=True
        )
    invoice_line_ids = fields.One2many(
        'account.invoice.line',
        'definitive_line_id',
        string='Invoice Lines',
        readonly=True
        )

    _constraints = [
    ]

    @api.one
    def _get_full_imputation(self):
        """Dummy function for dummy computed field that is used in a wizard"""
        self.full_imputation = False

    @api.one
    def _get_state(self):
        if self.invoice_line_ids:
            self.state = 'invoiced'
        else:
            self.state = 'draft'

    @api.one
    def write(self, vals):
        # No le pude encontrar la vuelta de porque algunas veces al guardar las
        # definitives se va a setear esto en cero y termina borrando los
        # vinculos desde las invoice lines a las definitives
        if 'invoice_line_ids' in vals:
            vals.pop('invoice_line_ids')
        return super(definitive_line, self).write(vals)

    @api.one
    @api.onchange('full_imputation')
    def _onchange_full_imputation(self):
        """This is used in the wizard to generate the invoice"""
        if self.full_imputation:
            self.to_invoice_amount = self.residual_amount
        else:
            self.to_invoice_amount = False

    @api.one
    @api.constrains(
        'residual_amount',
        'to_invoice_amount'
    )
    def _check_number(self):
        if self.residual_amount < self.to_invoice_amount:
            raise Warning(
                _("To Invoice Amount can't be greater than Residual Amount"))

    @api.one
    def unlink(self):
        if self.invoice_line_ids:
            raise Warning(_(
                "You can not delete a definitive line that has been invoiced"))
        return super(definitive_line, self).unlink()

    @api.one
    @api.depends(
        'amount',
        'invoice_line_ids',
    )
    def _get_amounts(self):
        """Update the following fields with the related values to the budget
        and the budget position:
        -invoiced_amount: amount sum of lines with a related invoice line
        -residual_amount: pending amount to be invoiced
        -to_pay_amount: amount sum of lines that has a related voucher in draft
        state
        -paid_amount: amount sum of lines that has a related voucher in open
        state
        """

        invoiced_amount = sum([
            invoice_line.price_subtotal
            for invoice_line in self.invoice_line_ids])
        to_pay_amount = sum([
            invoice_line.to_pay_amount
            for invoice_line in self.invoice_line_ids])
        paid_amount = sum([
            invoice_line.paid_amount
            for invoice_line in self.invoice_line_ids])
        self.invoiced_amount = invoiced_amount
        self.residual_amount = self.amount - invoiced_amount
        self.to_pay_amount = to_pay_amount
        self.paid_amount = paid_amount

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

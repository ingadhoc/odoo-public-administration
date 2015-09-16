# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class public_budget_definitive_make_invoice_detail(models.TransientModel):
    _name = "public_budget.definitive.make.invoice.detail"

    definitive_make_invoice_id = fields.Many2one(
        'public_budget.definitive.make.invoice',
        'Def Make Invoice',
    )
    definitive_line_id = fields.Many2one(
        'public_budget.definitive_line',
        'Def Make Invoice',
    )
    residual_amount = fields.Float(
        related='definitive_line_id.residual_amount',
    )
    to_invoice_amount = fields.Float(
        'Amount',
        digits=dp.get_precision('Account'),
    )
    full_imputation = fields.Boolean(
        'Full Imputation?',
    )

    @api.onchange('full_imputation')
    def change_full_imputation(self):
        self.to_invoice_amount = self.definitive_line_id.residual_amount

    @api.one
    @api.constrains(
        'residual_amount',
        'to_invoice_amount'
    )
    def _check_amounts(self):
        if self.residual_amount < self.to_invoice_amount:
            raise Warning(
                _("To Invoice Amount can't be greater than Residual Amount"))


class public_budget_definitive_make_invoice(models.TransientModel):
    _name = "public_budget.definitive.make.invoice"
    _description = "Transaction Definitive Make Invoice"

    @api.model
    def _get_default_journal(self):
        journal = self.env['account.journal'].search(
            [('type', '=', 'purchase'),
             ('company_id', '=', self._get_transaction_id().company_id.id)],
            limit=1)
        return journal

    @api.model
    @api.returns('public_budget.transaction')
    def _get_transaction_id(self):
        return self.env['public_budget.transaction'].browse(
            self._context.get('active_id', False))

    @api.model
    def _get_default_company(self):
        return self._get_transaction_id().company_id

    invoice_date = fields.Date(
        'Invoice Date',
        required=True
    )
    supplier_invoice_number = fields.Char(
        string='Supplier Invoice Number',
        help="The reference of this invoice as provided by the supplier.",
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=_get_default_company
    )
    supplier_ids = fields.Many2many(
        'res.partner',
        string='Suppliers',
        compute="_get_supplier_ids"
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        required=True,
        # context={'default_supplier': True}
    )
    line_ids = fields.One2many(
        'public_budget.definitive.make.invoice.detail',
        'definitive_make_invoice_id',
        string='Lines',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        domain="[('type', 'in', ('purchase','purchase_refund')),\
        ('company_id','=',company_id)]",
        default=_get_default_journal
    )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        'Transaction',
        default=_get_transaction_id,
        required=True
    )

    @api.one
    @api.depends('transaction_id')
    def _get_supplier_ids(self):
        self.supplier_ids = self.transaction_id.mapped(
            'preventive_line_ids.definitive_line_ids').filtered(
            lambda r: r.residual_amount != 0).mapped(
            'supplier_id')

    @api.one
    @api.onchange('supplier_id')
    def _compute_lines(self):
        self.line_ids = self.env[
            'public_budget.definitive.make.invoice.detail']
        transaction_id = self.env.context.get('active_id', False)
        if transaction_id:
            definitive_lines = self.env[
                'public_budget.definitive_line'].search([
                    ('transaction_id', '=', transaction_id),
                    ('supplier_id', '=', self.supplier_id.id),
                ])
            lines = []
            for line in definitive_lines:
                # No lo buscamos arriba porque no es un campo stored
                if line.residual_amount:
                    values = {
                        'definitive_line_id': line.id,
                        'definitive_make_invoice_id': self.id,
                    }
                    lines.append((0, _, values))
            self.line_ids = lines

    @api.multi
    def make_invoices(self):
        self.ensure_one()
        wizard = self

        tran_type = wizard.transaction_id.type_id
        advance_account = False
        if tran_type.with_advance_payment:
            if not tran_type.advance_account_id:
                raise Warning(_(
                    "On Advance Transactions, transaction advance type\
                    must have and advance account configured!"))
            advance_account = tran_type.advance_account_id
            # Check advance remaining amount
            total_to_invoice_amount = sum(
                wizard.mapped('line_ids.to_invoice_amount'))
            advance_to_return_amount = (
                wizard.transaction_id.advance_to_return_amount)
            if total_to_invoice_amount > advance_to_return_amount:
                raise Warning(_(
                    "You can not invoice more than Advance Remaining Amount!\n"
                    "* Amount to invoice: %s\n"
                    "* Advance Remaining Amount: %s"
                    ) % (total_to_invoice_amount, advance_to_return_amount))

        inv_lines = self.env['account.invoice.line']
        for line in wizard.line_ids.filtered(lambda r: r.to_invoice_amount):
            definitive_line = line.definitive_line_id
            line_vals = definitive_line.get_invoice_line_vals(
                line.to_invoice_amount)
            inv_lines += inv_lines.create(line_vals)

        # Si no hay se creo alguna linea es porque todas tienen amount 0
        if not inv_lines:
            raise Warning(_(
                "You should set at least one line with amount greater than 0"))

        invoice_vals = wizard.transaction_id.get_invoice_vals(
            wizard.supplier_id, wizard.journal_id, wizard.invoice_date,
            wizard.supplier_invoice_number, inv_lines, advance_account)

        invoice = self.env['account.invoice'].with_context(
            type='in_invoice').create(invoice_vals)

        # Buscamos la vista de supplier invoices
        action = self.env['ir.model.data'].xmlid_to_object(
            'account.action_invoice_tree2')

        if not action:
            return False
        res = action.read()[0]

        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'account.invoice_supplier_form')
        res['views'] = [(form_view_id, 'form')]
        res['res_id'] = invoice.id
        res['target'] = 'new'
        if tran_type.with_advance_payment:
            invoice.signal_workflow('invoice_open')
            return True
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

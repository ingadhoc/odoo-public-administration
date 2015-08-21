# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class public_budget_definitive_mass_invoice_create(models.TransientModel):
    _name = "public_budget.definitive.mass.invoice.create"
    _description = "Transaction Definitive Mass Invoice Create"

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
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=_get_default_company
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

    @api.multi
    def confirm(self):
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

        invoices = self.env['account.invoice']
        for definitive_line in self.transaction_id.mapped(
                'preventive_line_ids.definitive_line_ids').filtered(
                lambda r: r.residual_amount):
            line_vals = definitive_line.get_invoice_line_vals()
            inv_line = self.env['account.invoice.line'].create(line_vals)

            invoice_vals = wizard.transaction_id.get_invoice_vals(
                definitive_line.supplier_id, wizard.journal_id,
                wizard.invoice_date, False, inv_line, advance_account)

            invoices += invoices.create(invoice_vals)

        return invoices

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PublicBudgetDefinitiveMassInvoiceCreate(models.TransientModel):
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
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        default=_get_default_company
    )
    journal_id = fields.Many2one(
        'account.journal',
        required=True,
        domain="[('type', 'in', ('purchase','purchase_refund')),\
        ('company_id','=',company_id)]",
        default=_get_default_journal
    )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        default=_get_transaction_id,
        required=True
    )

    def confirm(self):
        self.ensure_one()
        msg = _('It is not possible to generate an invoice if '
                'the expedient of the transaction is not in a'
                ' permitted location of its user or is in transit')
        self.transaction_id.expedient_id\
            .check_location_allowed_for_current_user(msg)
        tran_type = self.transaction_id.type_id
        advance_account = False
        if tran_type.with_advance_payment:
            if not tran_type.advance_account_id:
                raise ValidationError(_(
                    "On Advance Transactions, transaction advance type"
                    "must have and advance account configured!"))
            advance_account = tran_type.advance_account_id

        invoices = self.env['account.move']
        for definitive_line in self.transaction_id.mapped(
                'preventive_line_ids.definitive_line_ids').filtered(
                lambda r: r.residual_amount):
            residual_amount = definitive_line.residual_amount
            if residual_amount < 0.0:
                invoice_type = 'in_refund'
            else:
                invoice_type = 'in_invoice'
            vals = definitive_line.get_invoice_line_vals(
                residual_amount, invoice_type=invoice_type)

            supplier = definitive_line.supplier_id
            invoice_vals = {
                'partner_id': supplier.id,
                'invoice_date': self.invoice_date,
                'invoice_line_ids': [(0, 0, vals)],
                'move_type': invoice_type,
                'journal_id': self.journal_id.id,
                'transaction_id': self.transaction_id.id,
            }
            invoices = invoices.create(invoice_vals)
            if invoices:
                invoices.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type
                    in ('receivable', 'payable'))._write(
                    {'account_id': (
                        advance_account and advance_account.id or
                        supplier.property_account_payable_id.id)})

        return True

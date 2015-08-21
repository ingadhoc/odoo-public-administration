# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class public_budget_definitive_mass_voucher_create(models.TransientModel):
    _name = "public_budget.definitive.mass.voucher.create"
    _description = "Transaction Definitive Mass voucher Create"

    # @api.model
    # def _get_default_journal(self):
    #     journal = self.env['account.journal'].search(
    #         [('type', '=', 'purchase'),
    #          ('company_id', '=', self._get_transaction_id().company_id.id)],
    #         limit=1)
    #     return journal

    @api.model
    @api.returns('public_budget.transaction')
    def _get_transaction_id(self):
        return self.env['public_budget.transaction'].browse(
            self._context.get('active_id', False))

    # @api.model
    # def _get_default_company(self):
    #     return self._get_transaction_id().company_id

    # payment_base_date = fields.Date(
    #     'Payment Base Date',
    #     required=True
    # )
    # company_id = fields.Many2one(
    #     'res.company',
    #     string='Company',
    #     default=_get_default_company
    # )
    # journal_id = fields.Many2one(
    #     'account.journal',
    #     string='Journal',
    #     required=True,
    #     domain="[('type', 'in', ('purchase','purchase_refund')),\
    #     ('company_id','=',company_id)]",
    #     default=_get_default_journal
    # )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        'Transaction',
        default=_get_transaction_id,
        required=True
    )

    @api.multi
    def confirm(self):
        self.ensure_one()
        # wizard = self
        # tran_type = wizard.transaction_id.type_id
        # advance_account = False
        # if tran_type.with_advance_payment:
        #     if not tran_type.advance_account_id:
        #         raise Warning(_(
        #             "On Advance Transactions, transaction advance type\
        #             must have and advance account configured!"))
        #     advance_account = tran_type.advance_account_id

        vouchers = self.env['account.voucher']
        for invoice in self.transaction_id.invoice_ids.filtered(
                lambda r: r.state == 'open'):
            # line_vals = definitive_line.get_voucher_line_vals()
            # inv_line = self.env['account.voucher.line'].create(line_vals)

            voucher_vals = {
                'type': 'payment',
                'partner_id': invoice.partner_id.id,
                'transaction_id': self.transaction_id.id,
                }
            # voucher_vals = wizard.transaction_id.get_voucher_vals(
                # definitive_line.supplier_id, wizard.journal_id,
                # wizard.voucher_date, False, inv_line, advance_account)

            vouchers += vouchers.create(voucher_vals)

        return vouchers

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

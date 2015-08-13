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
        domain=[('supplier', '=', True)],
        context={'default_supplier': True}
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
        self.supplier_ids = self.env['res.partner']
        definitive_lines = self.env[
            'public_budget.definitive_line'].search([
                ('preventive_line_id.transaction_id',
                    '=', self.transaction_id.id)])
        supplier_ids = []
        for line in definitive_lines:
            # No lo buscamos arriba porque no es un campo stored
            if line.residual_amount > 0:
                supplier_ids.append(line.supplier_id.id)
        self.supplier_ids = supplier_ids

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

    def make_invoices(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        invoice_obj = self.pool['account.invoice']
        inv_line_obj = self.pool['account.invoice.line']
        period_obj = self.pool.get('account.period')
        wizard = self.browse(cr, uid, ids[0], context=context)

        tran_type = wizard.transaction_id.type_id
        # advance_journal_id = False
        advance_account_id = False
        if tran_type.with_advance_payment:
            if not tran_type.advance_account_id:
                raise Warning(_(
                    "On Advance Transactions, transaction advance type\
                    must have and advance account configured!"))
            advance_account_id = tran_type.advance_account_id.id
            # Check advance remaining amount
            total_to_invoice_amount = sum([
                x.to_invoice_amount for x in wizard.line_ids])
            advance_to_return_amount = (
                wizard.transaction_id.advance_to_return_amount)
            if total_to_invoice_amount > advance_to_return_amount:
                raise Warning(_(
                    "You can not invoice more than Advance Remaining Amount!\n"
                    "* Amount to invoice: %s\n"
                    "* Advance Remaining Amount: %s"
                    ) % (total_to_invoice_amount, advance_to_return_amount))

        if context is None:
            context = {}
        inv_lines = []
        for line in wizard.line_ids:
            definitive_line = line.definitive_line_id
            preventive_line = definitive_line.preventive_line_id
            if line.to_invoice_amount:
                line_vals = {
                    'name': preventive_line.budget_position_id.name,
                    'price_unit': line.to_invoice_amount,
                    'quantity': 1,
                    'definitive_line_id': definitive_line.id,
                    'account_id': preventive_line.account_id.id,
                    # 'discount': ,
                    # 'product_id': line.product_id.id or False,
                    # 'uos_id': line.uos_id.id or False,
                    # 'sequence': line.sequence,
                }
                inv_lines.append(
                    inv_line_obj.create(cr, uid, line_vals, context=context))
                line.to_invoice_amount = False
        journal_type = wizard.journal_id.type
        if journal_type == 'sale':
            inv_type = 'out_invoice'
        elif journal_type == 'purchase':
            inv_type = 'in_invoice'
        elif journal_type == 'sale_refund':
            inv_type = 'out_refund'
        else:
            inv_type = 'in_refund'

        # Si no hay se creo alguna linea es porque todas tienen amount 0
        if not inv_lines:
            raise Warning(_(
                "You should set at least one line with amount greater than 0"))

        company_id = self.pool['res.users'].browse(
            cr, uid, uid, context=context).company_id.id
        partner_data = self.pool['account.invoice'].onchange_partner_id(
            cr, uid, False, inv_type,
            wizard.supplier_id.id, company_id=company_id)
        period_ids = period_obj.find(
            cr, uid, wizard.invoice_date, context=context)
        if advance_account_id:
            account_id = advance_account_id
        else:
            account_id = partner_data['value'].get('account_id', False)
        invoice_vals = {
            'partner_id': wizard.supplier_id.id,
            'date_invoice': wizard.invoice_date,
            'supplier_invoice_number': wizard.supplier_invoice_number,
            'invoice_line': [(6, 0, inv_lines)],
            # 'name': invoice.name,
            'type': inv_type,
            'account_id': account_id,
            # 'direct_payment_journal_id': advance_journal_id,
            'journal_id': wizard.journal_id.id,
            # 'currency_id': invoice.currency_id and invoice.currency_id.id,
            'fiscal_position': partner_data['value'].get(
                'fiscal_position', False),
            'payment_term': partner_data['value'].get('payment_term', False),
            'company_id': company_id,
            'transaction_id': wizard.transaction_id.id,
            'period_id': period_ids and period_ids[0] or False,
            'partner_bank_id': partner_data['value'].get(
                'partner_bank_id', False),
        }
        invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)

        # Buscamos la vista de supplier invoices
        result = mod_obj.get_object_reference(
            cr, uid, 'account', 'action_invoice_tree2')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        res = mod_obj.get_object_reference(
            cr, uid, 'account', 'invoice_supplier_form')
        result['views'] = [(res and res[1] or False, 'form')]
        result['res_id'] = invoice_id
        result['target'] = 'new'
        if tran_type.with_advance_payment:
            self.pool['account.invoice'].signal_workflow(
                cr, uid, [invoice_id], 'invoice_open')
            return True
        # result['res_id'] = invoice_id
        # result['view_mode'] = 'form'
        # result['view_id'] = 'account.invoice_supplier_form'
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

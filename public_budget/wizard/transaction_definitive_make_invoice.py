# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class public_budget_definitive_make_invoice_detail(models.TransientModel):
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
        readonly=True,
    )

    @api.onchange('full_imputation')
    def change_full_imputation(self):
        self.to_invoice_amount = self.definitive_line_id.residual_amount

    @api.one
    @api.constrains(
        'to_invoice_amount'
    )
    def _check_amounts(self):
        if self.residual_amount < self.to_invoice_amount:
            raise ValidationError(
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
        domain="[('type', 'in', ('purchase','purchase_refund')),"
        "('company_id','=',company_id)]",
        default=_get_default_journal
    )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        'Transaction',
        default=_get_transaction_id,
        required=True
    )
    use_documents = fields.Boolean(
        related='journal_id.use_documents',
        string='Use Documents?',
        readonly=True,
    )
    journal_document_type_id = fields.Many2one(
        'account.journal.document.type',
        'Document Type',
        ondelete='cascade',
    )
    document_sequence_id = fields.Many2one(
        related='journal_document_type_id.sequence_id',
        readonly=True,
    )
    document_number = fields.Char(
        string='Document Number',
    )
    available_journal_document_type_ids = fields.Many2many(
        'account.journal.document.type',
        compute='get_available_journal_document_types',
        string='Available Journal Document Types',
    )
    # is_refund = fields.Boolean(
    #     'Is Refund?',
    # )
    to_invoice_amount = fields.Float(
        compute='_compute_to_invoice_amount',
    )

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        """
        Idea obtenida de aca
        https://github.com/odoo/odoo/issues/16072#issuecomment-289833419
        por el cambio que se introdujo en esa mimsa conversación, TODO en v11
        no haría mas falta, simplemente domain="[('id', 'in', x2m_field)]"
        Otras posibilidades que probamos pero no resultaron del todo fue:
        * agregar onchange sobre campos calculados y que devuelvan un dict con
        domain. El tema es que si se entra a un registro guardado el onchange
        no se ejecuta
        * usae el modulo de web_domain_field que esta en un pr a la oca
        """
        for field in field_onchange.keys():
            if field.startswith((
                    'available_journal_document_type_ids.', 'supplier_ids')):
                del field_onchange[field]
        return super(public_budget_definitive_make_invoice, self).onchange(
            values, field_name, field_onchange)

    @api.onchange('document_number', 'journal_document_type_id')
    def onchange_document_number(self):
        # if we have a sequence, number is set by sequence and we dont check
        sequence = self.journal_document_type_id.sequence_id
        document_type = self.journal_document_type_id.document_type_id
        if not sequence and document_type:
            res = document_type.validate_document_number(self.document_number)
            if res and res != self.document_number:
                self.document_number = res

    @api.multi
    @api.depends('line_ids.to_invoice_amount')
    def _compute_to_invoice_amount(self):
        for rec in self:
            rec.to_invoice_amount = sum(
                rec.mapped('line_ids.to_invoice_amount'))

    @api.multi
    @api.depends('journal_id', 'supplier_id', 'to_invoice_amount')
    def get_available_journal_document_types(self):
        for rec in self:
            if not rec.journal_id or not rec.supplier_id:
                continue
            # desde el wizard se pueden crear facturas o reembolsos
            if rec.to_invoice_amount < 0.0:
                invoice_type = 'in_refund'
            else:
                invoice_type = 'in_invoice'
            res = rec.env[
                'account.invoice']._get_available_journal_document_types(
                rec.journal_id, invoice_type, rec.supplier_id)
            rec.available_journal_document_type_ids = res[
                'available_journal_document_types']
            rec.journal_document_type_id = res[
                'journal_document_type']

    @api.one
    @api.depends('transaction_id')
    def _get_supplier_ids(self):
        suppliers = self.transaction_id.mapped(
            'preventive_line_ids.definitive_line_ids').filtered(
            lambda r: r.residual_amount != 0).mapped(
            'supplier_id')
        self.supplier_ids = suppliers
        if len(suppliers) == 1:
            self.supplier_id = suppliers.id

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

        tran_type = self.transaction_id.type_id
        advance_account = False
        if self.to_invoice_amount < 0.0:
            invoice_type = 'in_refund'
        else:
            invoice_type = 'in_invoice'
        if tran_type.with_advance_payment:
            if not tran_type.advance_account_id:
                raise ValidationError(_(
                    "On Advance Transactions, transaction advance type"
                    "must have and advance account configured!"))
            advance_account = tran_type.advance_account_id
            # Check advance remaining amount
            advance_to_return_amount = (
                self.transaction_id.advance_to_return_amount)
            if self.to_invoice_amount > advance_to_return_amount:
                raise ValidationError(_(
                    "You can not invoice more than Advance Remaining Amount!\n"
                    "* Amount to invoice: %s\n"
                    "* Advance Remaining Amount: %s") % (
                    self.to_invoice_amount, advance_to_return_amount))

        inv_lines = self.env['account.invoice.line']
        for line in self.line_ids.filtered(lambda r: r.to_invoice_amount):
            definitive_line = line.definitive_line_id
            line_vals = definitive_line.get_invoice_line_vals(
                line.to_invoice_amount, invoice_type=invoice_type)
            inv_lines += inv_lines.create(line_vals)

        # Si no hay se creo alguna linea es porque todas tienen amount 0
        if not inv_lines:
            raise ValidationError(_(
                "You should set at least one line with amount greater than 0"))

        invoice_vals = {
            'partner_id': self.supplier_id.id,
            'date_invoice': self.invoice_date,
            'document_number': self.document_number,
            'journal_document_type_id': self.journal_document_type_id.id,
            'invoice_line_ids': [(6, 0, inv_lines.ids)],
            'type': invoice_type,
            'account_id': (
                advance_account and advance_account.id or
                self.supplier_id.property_account_payable_id.id),
            'journal_id': self.journal_id.id,
            'company_id': self.journal_id.company_id.id,
            'transaction_id': self.transaction_id.id,
        }

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

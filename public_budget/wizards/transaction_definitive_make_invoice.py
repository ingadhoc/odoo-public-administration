from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PublicBudgetDefinitiveMakeInvoice(models.TransientModel):
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
        compute="_compute_supplier_ids"
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
        related='journal_id.l10n_latam_use_documents',
        string='Use Documents?',
    )
    journal_document_type_id = fields.Many2one(
        'l10n_latam.document.type',
        'Document Type',
        ondelete='cascade',
    )
    document_sequence = fields.Integer(
        related='journal_document_type_id.sequence',
    )
    document_number = fields.Char(
    )
    available_journal_document_type_ids = fields.Many2many(
        'l10n_latam.document.type',
        compute='_compute_available_journal_document_types',
        string='Available Journal Document Types',
    )
    # is_refund = fields.Boolean(
    #     'Is Refund?',
    # )
    to_invoice_amount = fields.Monetary(
        compute='_compute_to_invoice_amount',
    )
    currency_id = fields.Many2one(
        related='line_ids.currency_id',
        readonly=True,
    )

    @api.onchange('document_number', 'journal_document_type_id')
    def onchange_document_number(self):
        # if we have a sequence, number is set by sequence and we dont check
        sequence = self.journal_document_type_id.sequence
        document_type = self.journal_document_type_id
        if not sequence and document_type:
            res = document_type._format_document_number(self.document_number)
            if res and res != self.document_number:
                self.document_number = res

    @api.depends('line_ids.to_invoice_amount')
    def _compute_to_invoice_amount(self):
        for rec in self:
            rec.to_invoice_amount = sum(
                rec.mapped('line_ids.to_invoice_amount'))

    @api.depends('journal_id', 'supplier_id', 'to_invoice_amount')
    def _compute_available_journal_document_types(self):
        for rec in self:
            rec.available_journal_document_type_ids = self.env['l10n_latam.document.type']
            rec.journal_document_type_id = self.env['l10n_latam.document.type']
            if not rec.journal_id or not rec.supplier_id:
                continue
            # desde el wizard se pueden crear facturas o reembolsos
            if rec.to_invoice_amount < 0.0:
                invoice_type = 'in_refund'
            else:
                invoice_type = 'in_invoice'
            move = rec.env['account.move'].new({
                'journal_id': rec.journal_id.id,
                'type': invoice_type,
                'l10n_latam_use_documents': rec.use_documents,
                'partner_id': rec.supplier_id.id,
            })
            rec.available_journal_document_type_ids = move.l10n_latam_available_document_type_ids
            rec.journal_document_type_id = move.l10n_latam_document_type_id

    @api.onchange('supplier_ids')
    def _onchange_suppliers(self):
        # TODO en v13 podemos hacer como en documents types y convertir esto a
        # computed para que se setee en create/write
        if not self.supplier_id and len(self.supplier_ids) == 1:
            self.supplier_id = self.supplier_ids.id

    @api.depends('transaction_id')
    def _compute_supplier_ids(self):
        for rec in self:
            definitive_lines = rec.transaction_id.mapped(
                'preventive_line_ids.definitive_line_ids')
            # TODO analice if are necessary in future version
            env_all_mode = definitive_lines.env.all.mode
            definitive_lines.env.all.mode = True
            suppliers = definitive_lines.filtered(
                lambda r: r.residual_amount != 0).mapped('supplier_id')
            rec.supplier_ids = suppliers
            definitive_lines.env.all.mode = env_all_mode

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
                    ('residual_amount', '!=', 0.0),
                ])
            lines = []
            for line in definitive_lines:
                values = {
                    'definitive_line_id': line.id,
                    'definitive_make_invoice_id': self.id,
                }
                lines.append((0, _, values))
            self.line_ids = lines

    def make_invoices(self):
        self.ensure_one()
        msg = _('It is not possible to generate an invoice if '
                'the expedient of the transaction is not in a'
                ' permitted location of its user or is in transit')
        self.transaction_id.expedient_id\
            .check_location_allowed_for_current_user(msg)
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
            if self.currency_id.compare_amounts(
                    self.to_invoice_amount, advance_to_return_amount) == 1:
                raise ValidationError(_(
                    "You can not invoice more than Advance Remaining Amount!\n"
                    "* Amount to invoice: %s\n"
                    "* Advance Remaining Amount: %s") % (
                    self.to_invoice_amount, advance_to_return_amount))

        list_inv_lines = []
        for line in self.line_ids.filtered(lambda r: r.to_invoice_amount):
            definitive_line = line.definitive_line_id
            list_inv_lines.append((0, 0, definitive_line.get_invoice_line_vals(
                line.to_invoice_amount, invoice_type=invoice_type)))

        # Si no hay se creo alguna linea es porque todas tienen amount 0
        if not list_inv_lines:
            raise ValidationError(_(
                "You should set at least one line with amount greater than 0"))

        invoice_vals = {
            'partner_id': self.supplier_id.id,
            'invoice_date': self.invoice_date,
            'l10n_latam_document_number': self.document_number,
            'l10n_latam_document_type_id': self.journal_document_type_id.id,
            'invoice_line_ids': list_inv_lines,
            'type': invoice_type,
            'journal_id': self.journal_id.id,
            'transaction_id': self.transaction_id.id,
        }

        invoice = self.env['account.move'].create(invoice_vals)
        if invoice:
            invoice.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type
                in ('receivable', 'payable'))._write(
                {'account_id': (
                    advance_account and advance_account.id or
                    self.supplier_id.property_account_payable_id.id)
                 })
        # Buscamos la vista de supplier invoices
        action = self.env.ref('account.action_move_in_invoice_type')

        if not action:
            return False
        res = action.read()[0]

        form_view_id = self.env.ref('account.view_move_form').id
        res['views'] = [(form_view_id, 'form')]
        res['res_id'] = invoice.id
        res['target'] = 'new'
        if tran_type.with_advance_payment:
            invoice.post()
            return True
        return res

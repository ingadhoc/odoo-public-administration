from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from lxml import etree
import logging
_logger = logging.getLogger(__name__)


class DefinitiveLine(models.Model):

    _name = 'public_budget.definitive_line'
    _description = 'Definitive Line'
    _rec_name = 'preventive_line_id'

    issue_date = fields.Date(
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today
    )
    supplier_id = fields.Many2one(
        'res.partner',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    amount = fields.Monetary(
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    residual_amount = fields.Monetary(
        compute='_compute_residual_amount',
        store=True,
    )
    to_pay_amount = fields.Monetary(
        compute='_compute_amounts',
        store=True,
    )
    to_pay_amount_dynamic = fields.Monetary(
        compute='_compute_amounts_dynamic',
    )
    paid_amount = fields.Monetary(
        compute='_compute_amounts',
        store=True,
    )
    paid_amount_dynamic = fields.Monetary(
        compute='_compute_amounts_dynamic',
    )
    invoiced_amount = fields.Monetary(
        compute='_compute_amounts',
        store=True,
    )
    invoiced_amount_dynamic = fields.Monetary(
        compute='_compute_amounts_dynamic',
    )
    preventive_line_id = fields.Many2one(
        'public_budget.preventive_line',
        ondelete='cascade',
        required=True,
        auto_join=True,
    )
    transaction_id = fields.Many2one(
        store=True,
        related='preventive_line_id.transaction_id',
        auto_join=True,
    )
    currency_id = fields.Many2one(
        related='transaction_id.currency_id',
    )
    budget_id = fields.Many2one(
        store=True,
        related='preventive_line_id.budget_id',
        auto_join=True,
    )
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('invoiced', 'Invoiced')],
        string='State',
        # default necesario para que deje crear ni bien se genera la linea
        default='draft',
        compute='_compute_state',
        store=True,
    )
    invoice_line_ids = fields.One2many(
        'account.move.line',
        'definitive_line_id',
        readonly=True,
        auto_join=True,
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        related='transaction_id.expedient_id',
        store=True,
    )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        related='preventive_line_id.budget_position_id',
        store=True,
    )

    @api.constrains('issue_date')
    def check_dates(self):
        for rec in self:
            if rec.issue_date < rec.transaction_id.issue_date:
                raise ValidationError(_(
                    'La fecha de la línea definitiva debe ser mayor a la fecha'
                    ' de la transacción'))

    @api.depends('invoice_line_ids')
    def _compute_state(self):
        for rec in self:
            _logger.info('Getting state for definitive line %s' % rec.id)
            if rec.invoice_line_ids:
                rec.state = 'invoiced'
            else:
                rec.state = 'draft'

    def write(self, vals):
        # TODO ver si se puede sacar esto.
        # No le pude encontrar la vuelta de porque algunas veces al guardar las
        # definitives se va a setear esto en cero y termina borrando los
        # vinculos desde las invoice lines a las definitives
        if 'invoice_line_ids' in vals:
            vals.pop('invoice_line_ids')
        return super().write(vals)

    def unlink(self):
        if self.filtered('invoice_line_ids'):
            raise ValidationError(_(
                "You can not delete a definitive line that has been "
                "invoiced"))
        return super().unlink()

    @api.depends('amount', 'invoiced_amount')
    def _compute_residual_amount(self):
        for rec in self:
            rec.residual_amount = rec.amount - rec.invoiced_amount

    @api.depends(
        'invoice_line_ids.move_id.state',
        'invoice_line_ids.move_id.payment_state',
        'invoice_line_ids.move_id.to_pay_amount',
        'invoice_line_ids.move_id.amount_residual',
    )
    def _compute_amounts_dynamic(self):
        _logger.info(
            'Getting dynamic amounts for definitive lines %s' % self.ids)
        if not self._context.get('analysis_to_date', False):
            for rec in self:
                rec.invoiced_amount_dynamic = rec.invoiced_amount
                rec.to_pay_amount_dynamic = rec.to_pay_amount
                rec.paid_amount_dynamic = rec.paid_amount
        else:
            for rec in self:
                amounts = rec._get_amounts()
                rec.invoiced_amount_dynamic = amounts['invoiced_amount']
                rec.to_pay_amount_dynamic = amounts['to_pay_amount']
                rec.paid_amount_dynamic = amounts['paid_amount']

    @api.depends(
        'invoice_line_ids.move_id.state',
        'invoice_line_ids.move_id.payment_state',
        'invoice_line_ids.move_id.to_pay_amount',
        'invoice_line_ids.move_id.amount_residual',
    )
    def _compute_amounts(self):
        """Update the following fields with the related values to the budget
        and the budget position:
        -invoiced_amount: amount sum of lines with a related invoice line
        -residual_amount: pending amount to be invoiced
        -to_pay_amount: amount sum of lines that has a related payment in draft
        state
        -paid_amount: amount sum of lines that has a related payment in open
        state
        """
        _logger.info('Getting amounts for definitive lines %s' % self.ids)
        for rec in self:
            amounts = rec._get_amounts()
            rec.invoiced_amount = amounts['invoiced_amount']
            rec.to_pay_amount = amounts['to_pay_amount']
            rec.paid_amount = amounts['paid_amount']
        _logger.debug(
            'Finish getting amounts for definitive lines %s' % self.ids)

    def _get_amounts(self):
        self.ensure_one()
        invoice_lines = self.invoice_line_ids.filtered(
            lambda x: x.move_id.state not in ('cancel', 'draft'))

        to_date = self._context.get('analysis_to_date', False)
        if to_date:
            to_date = fields.Date.from_string(to_date)
            invoice_lines.filtered(lambda x: x.move_id.invoice_date <= to_date)

        debit_invoice_lines = invoice_lines.filtered(
            lambda x: x.move_id.move_type in ['out_refund', 'in_invoice'])
        credit_invoice_lines = invoice_lines.filtered(
            lambda x: x.move_id.move_type in ['out_invoice', 'in_refund'])

        # all computed fields, no problem for analysis to date
        invoiced_amount = sum(debit_invoice_lines.mapped('price_subtotal'))
        to_pay_amount = sum(debit_invoice_lines.mapped('to_pay_amount'))
        paid_amount = sum(debit_invoice_lines.mapped('paid_amount'))

        invoiced_amount -= sum(credit_invoice_lines.mapped('price_subtotal'))
        to_pay_amount -= sum(credit_invoice_lines.mapped('to_pay_amount'))
        paid_amount -= sum(credit_invoice_lines.mapped('paid_amount'))

        return {
            'invoiced_amount': invoiced_amount,
            'to_pay_amount': to_pay_amount,
            'paid_amount': paid_amount,
        }

    def get_invoice_line_vals(
            self, to_invoice_amount, invoice_type=False):
        self.ensure_one()
        if invoice_type in ('in_refund', 'out_refund'):
            to_invoice_amount = -1.0 * to_invoice_amount
        preventive_line = self.preventive_line_id
        line_vals = {
            'name': preventive_line.budget_position_id.name,
            'price_unit': to_invoice_amount,
            'quantity': 1,
            'definitive_line_id': self.id,
            'account_id': preventive_line.account_id.id,
            # 'discount': ,
            # 'product_id': line.product_id.id or False,
            # 'uos_id': line.uos_id.id or False,
            # 'sequence': line.sequence,
        }
        return line_vals

    @api.constrains('amount')
    def check_budget_state_open(self):
        if any(self.filtered(lambda x: x.budget_id and x.budget_id.state != 'open')):
            raise ValidationError(_(
                'Solo puede cambiar afectaciones definitivas si '
                'el presupuesto está abierto'))

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form', toolbar=False,
            submenu=False):
        """
        Modificamos vista de definitive lines para que segun el partner type
        cambie el dominio del partner
        """
        result = super().fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        definitive_partner_type = self._context.get(
            'default_definitive_partner_type')
        if definitive_partner_type == 'subsidy_recipient':
            doc = etree.XML(result['arch'])
            node = doc.xpath("//field[@name='supplier_id']")[0]
            node.set('domain', "[('subsidy_recipient', '=', True)]")
            result['arch'] = etree.tostring(doc)
        return result

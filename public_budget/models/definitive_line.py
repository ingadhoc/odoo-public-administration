# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
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
        string='Supplier',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        context={'default_supplier': True},
        domain=[('supplier', '=', True)]
    )
    amount = fields.Monetary(
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    residual_amount = fields.Monetary(
        compute='_get_residual_amount',
        store=True,
    )
    to_pay_amount = fields.Monetary(
    )
    paid_amount = fields.Monetary(
    )
    invoiced_amount = fields.Monetary(
    )
    computed_to_pay_amount = fields.Monetary(
        string='To Pay Amount',
        compute='_get_computed_amounts',
    )
    computed_paid_amount = fields.Monetary(
        string='Paid Amount',
        compute='_get_computed_amounts',
    )
    computed_invoiced_amount = fields.Monetary(
        string='Invoiced Amount',
        compute='_get_computed_amounts',
    )
    preventive_line_id = fields.Many2one(
        'public_budget.preventive_line',
        ondelete='cascade',
        string='Preventive Line',
        required=True,
        auto_join=True,
    )
    transaction_id = fields.Many2one(
        readonly=True,
        store=True,
        related='preventive_line_id.transaction_id',
        auto_join=True,
    )
    currency_id = fields.Many2one(
        related='transaction_id.currency_id',
        readonly=True,
    )
    budget_id = fields.Many2one(
        readonly=True,
        store=True,
        related='preventive_line_id.budget_id',
        auto_join=True,
    )
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('invoiced', 'Invoiced')],
        string='State',
        compute='_get_state',
        store=True,
    )
    invoice_line_ids = fields.One2many(
        'account.invoice.line',
        'definitive_line_id',
        string='Invoice Lines',
        readonly=True,
        auto_join=True,
    )

    @api.multi
    @api.constrains('issue_date')
    def check_dates(self):
        for rec in self:
            if rec.issue_date < rec.transaction_id.issue_date:
                raise ValidationError(_(
                    'La fecha de la línea definitiva debe ser mayor a la fecha'
                    ' de la transacción'))

    @api.multi
    @api.depends('invoice_line_ids')
    def _get_state(self):
        for rec in self:
            _logger.info('Getting state for definitive line %s' % rec.id)
            if rec.invoice_line_ids:
                rec.state = 'invoiced'
            else:
                rec.state = 'draft'

    @api.multi
    def write(self, vals):
        # TODO ver si se puede sacar esto.
        # No le pude encontrar la vuelta de porque algunas veces al guardar las
        # definitives se va a setear esto en cero y termina borrando los
        # vinculos desde las invoice lines a las definitives
        if 'invoice_line_ids' in vals:
            vals.pop('invoice_line_ids')
        return super(DefinitiveLine, self).write(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.invoice_line_ids:
                raise ValidationError(_(
                    "You can not delete a definitive line that has been "
                    "invoiced"))
        return super(DefinitiveLine, self).unlink()

    @api.multi
    @api.depends('amount', 'invoiced_amount')
    def _get_residual_amount(self):
        for rec in self:
            rec.residual_amount = rec.amount - rec.invoiced_amount

    @api.multi
    def _get_computed_amounts(self):
        # computed fields for to date anlysis
        for rec in self:
            invoiced_amount, to_pay_amount, paid_amount = (
                rec._get_amounts_to_date())
            rec.computed_invoiced_amount = invoiced_amount
            rec.computed_to_pay_amount = to_pay_amount
            rec.computed_paid_amount = paid_amount

    @api.multi
    def _get_amounts(self):
        # normal fields for good performance
        for rec in self:
            invoiced_amount, to_pay_amount, paid_amount = (
                rec._get_amounts_to_date())
            rec.invoiced_amount = invoiced_amount
            rec.to_pay_amount = to_pay_amount
            rec.paid_amount = paid_amount

    @api.multi
    def _get_amounts_to_date(self):
        """Update the following fields with the related values to the budget
        and the budget position:
        -invoiced_amount: amount sum of lines with a related invoice line
        -residual_amount: pending amount to be invoiced
        -to_pay_amount: amount sum of lines that has a related payment in draft
        state
        -paid_amount: amount sum of lines that has a related payment in open
        state
        """
        self.ensure_one()
        _logger.info('Getting amounts for definitive line %s' % self.id)

        filter_domain = [
            ('id', 'in', self.invoice_line_ids.ids),
            ('invoice_id.state', 'not in', ('cancel', 'draft'))
        ]

        # Add this to allow analysis between dates
        to_date = self._context.get('analysis_to_date', False)

        if to_date:
            filter_domain += [('invoice_id.date_invoice', '<=', to_date)]
        # TODO borrar esto que no seria necesario porque forzamos recalculo
        # en invoice.py con self.invoice_line._get_amounts()
        # else:
        #     # we invalidate cache because of invoice line computed fields
        #     self.invalidate_cache()

        debit_filter_domain = filter_domain + [
            ('invoice_id.type', 'in', ('out_refund', 'in_invoice'))]
        credit_filter_domain = filter_domain + [
            ('invoice_id.type', 'in', ('out_invoice', 'in_refund'))]
        debit_invoice_lines = self.invoice_line_ids.search(
            debit_filter_domain)
        credit_invoice_lines = self.invoice_line_ids.search(
            credit_filter_domain)

        # all computed fields, no problem for analysis to date
        invoiced_amount = to_pay_amount = paid_amount = 0
        for dil in debit_invoice_lines:
            invoiced_amount += dil.price_subtotal
            to_pay_amount += dil.to_pay_amount
            paid_amount += dil.paid_amount
        for cil in credit_invoice_lines:
            invoiced_amount -= cil.price_subtotal
            to_pay_amount -= cil.to_pay_amount
            paid_amount -= cil.paid_amount

        _logger.info('Finish getting amounts for definitive line %s' % self.id)
        return (invoiced_amount, to_pay_amount, paid_amount)

    @api.multi
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

    @api.multi
    @api.constrains(
        'amount')
    def check_budget_state_open(self):
        for rec in self:
            if rec.budget_id and rec.budget_id.state not in 'open':
                raise ValidationError(
                    'Solo puede cambiar afectaciones definitivas si '
                    'el presupuesto está abierto')

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form', toolbar=False,
            submenu=False):
        """
        Modificamos vista de definitive lines para que segun el partner type
        cambie el dominio del partner
        """
        result = super(DefinitiveLine, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        definitive_partner_type = self._context.get('definitive_partner_type')
        if definitive_partner_type == 'subsidy_recipient':
            doc = etree.XML(result['arch'])
            node = doc.xpath("//field[@name='supplier_id']")[0]
            node.set('domain', "[('subsidy_recipient', '=', True)]")
            result['arch'] = etree.tostring(doc)
        return result

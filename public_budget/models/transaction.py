from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero
import logging
_logger = logging.getLogger(__name__)


class BudgetTransaction(models.Model):

    _name = 'public_budget.transaction'
    _description = 'Budget Transaction'

    _order = "id desc"

    _states_ = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancel', 'Cancel'),
    ]

    @api.model
    def _get_default_budget(self):
        budgets = self.env['public_budget.budget'].search(
            [('state', '=', 'open')])
        return budgets and budgets[0] or False

    issue_date = fields.Date(
        readonly=True,
        required=True,
        default=fields.Date.context_today,
        states={'draft': [('readonly', False)]},
    )
    name = fields.Char(
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]}
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        readonly=True,
        required=True,
        default=lambda self: self.env.user
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expedient',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )
    budget_id = fields.Many2one(
        'public_budget.budget',
        string='Budget',
        required=True,
        default=_get_default_budget,
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('state', '=', 'open')],
        auto_join=True,
    )
    type_id = fields.Many2one(
        'public_budget.transaction_type',
        string='Type',
        readonly=True,
        required=True,
        domain="[('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]}
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    note = fields.Html(
    )
    type_with_advance_payment = fields.Boolean(
        readonly=True,
        related='type_id.with_advance_payment'
    )
    definitive_line_ids = fields.One2many(
        comodel_name='public_budget.definitive_line',
        inverse_name='transaction_id',
        string='Definitive Lines',
        readonly=True,
        auto_join=True,
    )
    supplier_ids = fields.Many2many(
        relation='transaction_res_partner_rel',
        comodel_name='res.partner',
        string='Suppliers',
        store=True,
        compute='_get_suppliers'
    )
    budget_position_ids = fields.Many2many(
        relation='transaction_position_rel',
        comodel_name='public_budget.budget_position',
        string='Related Budget Positions',
        store=True,
        compute='_get_budget_positions',
        auto_join=True,
    )
    advance_preventive_line_ids = fields.One2many(
        comodel_name='public_budget.preventive_line',
        inverse_name='transaction_id',
        string='Advance Preventive Lines',
        readonly=True,
        states={'open': [('readonly', False)]},
        context={
            'default_advance_line': 1,
            'default_preventive_status': 'confirmed',
            'advance_line': 1},
        domain=[('advance_line', '=', True)],
        auto_join=True,
    )
    preventive_amount = fields.Monetary(
        string='Monto Preventivo',
        compute='_get_preventive_amount',
        store=True,
    )
    preventive_balance = fields.Monetary(
        string='Saldo Preventivo',
        compute='_get_preventive_balance',
        store=True,
        help='Saldo Preventivo',
    )
    definitive_balance = fields.Monetary(
        string='Saldo Definitivo',
        compute='_get_definitive_balance',
        store=True,
        help='Saldo Definitivo',
    )
    definitive_amount = fields.Monetary(
        string='Monto Definitivo',
        compute='_get_definitive_amount',
        store=True,
    )
    invoiced_amount = fields.Monetary(
        string='Monto Devengado',
        compute='_get_invoiced_amount',
        store=True,
    )
    invoiced_balance = fields.Monetary(
        string='Saldo Devengado',
        compute='_get_invoiced_balance',
        store=True,
    )
    to_pay_amount = fields.Monetary(
        string='Monto A Pagar',
        compute='_get_to_pay_amount',
        store=True,
    )
    to_pay_balance = fields.Monetary(
        string='Saldo A Pagar',
        compute='_get_to_pay_balance',
        store=True,
    )
    paid_amount = fields.Monetary(
        string='Monto Pagado',
        compute='_get_paid_amount',
        store=True,
    )
    advance_preventive_amount = fields.Monetary(
        string='Monto Preventivo de Adelanto',
        compute='_get_advance_preventive_amount',
        store=True,
    )
    advance_to_pay_amount = fields.Monetary(
        string='Monto de Adelanto a Pagar',
        compute='_get_advance_amounts',
        store=True,
    )
    advance_paid_amount = fields.Monetary(
        string='Monto de Adelanto Pagado',
        compute='_get_advance_amounts',
        store=True,
    )
    advance_remaining_amount = fields.Monetary(
        string='Monto Remanente de Adelanto',
        compute='_compute_advance_remaining_amount',
        store=True,
    )
    advance_to_return_amount = fields.Monetary(
        string='Monto a Devolver',
        compute='_get_advance_to_return_amount',
        store=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'public_budget.transaction')
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True,
    )
    user_location_ids = fields.Many2many(
        'public_budget.location',
        compute='_compute_user_locations',
    )
    state = fields.Selection(
        _states_,
        'State',
        default='draft',
    )
    preventive_line_ids = fields.One2many(
        'public_budget.preventive_line',
        'transaction_id',
        string='Preventive Lines',
        readonly=True,
        auto_join=True,
        states={'open': [('readonly', False)]},
        domain=[('advance_line', '=', False)]
    )
    invoice_ids = fields.One2many(
        'account.invoice',
        'transaction_id',
        string='Invoices',
        readonly=True,
        auto_join=True,
        states={'open': [('readonly', False)]}
    )
    definitive_partner_type = fields.Selection(
        related='type_id.definitive_partner_type'
    )
    payment_group_ids = fields.One2many(
        'account.payment.group',
        'transaction_id',
        string='Payment Orders',
        readonly=True,
        context={'default_partner_type': 'supplier'},
        states={'open': [('readonly', False)]},
        auto_join=True,
        domain=[
            ('partner_type', '=', 'supplier'),
            ('transaction_with_advance_payment', '=', False)
        ],
    )
    # Usamos otro campo por que si no el depends de advance_payment_group_ids
    # se toma en cuenta igual que si fuese el de payments y necesitamos que sea
    # distinto para que no recalcule tantas veces. Si no la idea sería que
    # sea basicamente es el mismo campo de arriba pero lo separamos para poner
    # en otro lugar de la vista
    advance_payment_group_ids = fields.One2many(
        'account.payment.group',
        'transaction_id',
        string='Advance Payment Orders',
        readonly=True,
        domain=[
            ('partner_type', '=', 'supplier'),
            ('transaction_with_advance_payment', '=', True)
        ],
        context={'default_partner_type': 'supplier'},
        auto_join=True,
        states={'open': [('readonly', False)]},
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
            if field.startswith('user_location_ids.'):
                del field_onchange[field]
        return super(BudgetTransaction, self).onchange(
            values, field_name, field_onchange)

    @api.multi
    # dummy depends to compute values on create
    @api.depends('company_id')
    def _compute_user_locations(self):
        for rec in self:
            rec.user_location_ids = rec.env.user.location_ids.ids

    @api.multi
    @api.constrains('type_id', 'company_id')
    def check_type_company(self):
        for rec in self:
            if rec.type_id.company_id != rec.company_id:
                raise ValidationError(_(
                    'Company must be the same as Type Company!'))

    @api.multi
    @api.depends(
        'partner_id',
        'preventive_line_ids.definitive_line_ids.supplier_id',
    )
    def _get_suppliers(self):
        for rec in self:
            definitive_lines = rec.env['public_budget.definitive_line'].search(
                [('preventive_line_id.transaction_id', '=', rec.id)])
            rec.supplier_ids = definitive_lines.mapped('supplier_id')

    @api.multi
    @api.depends(
        'preventive_line_ids.budget_position_id',
    )
    def _get_budget_positions(self):
        for rec in self:
            rec.budget_position_ids = rec.preventive_line_ids.mapped(
                'budget_position_id')

    @api.multi
    @api.depends(
        # TODO este depends puede hacer que se recalcule todo al crear un
        # payment group
        'invoiced_amount',
        'advance_paid_amount',
    )
    def _get_advance_to_return_amount(self):
        _logger.info('Getting Transaction Advance To Return Amount')
        for rec in self:
            rec.advance_to_return_amount = (
                rec.advance_paid_amount - rec.invoiced_amount)

    @api.multi
    @api.depends(
        'advance_preventive_line_ids.preventive_amount',
    )
    def _get_advance_preventive_amount(self):
        _logger.info('Getting Transaction Advance Preventive Amount')
        for rec in self:
            advance_preventive_amount = sum(rec.mapped(
                'advance_preventive_line_ids.preventive_amount'))
            rec.advance_preventive_amount = advance_preventive_amount

    @api.multi
    @api.depends(
        # TODO ver que esto no deberia llamarse tantas veces
        'advance_preventive_amount',
        'advance_to_pay_amount',
    )
    def _compute_advance_remaining_amount(self):
        _logger.info('Getting Transaction Advance Remaining Amount')
        for rec in self:
            rec.advance_remaining_amount = (
                rec.advance_preventive_amount - rec.advance_to_pay_amount)

    @api.multi
    @api.depends(
        'advance_payment_group_ids.state',
    )
    def _get_advance_amounts(self):
        _logger.info('Getting Transaction Advance Amounts')
        to_date = self._context.get('analysis_to_date', False)
        for rec in self:
            if not rec.advance_payment_group_ids:
                continue

            domain = [('id', 'in', rec.advance_payment_group_ids.ids)]
            to_pay_domain = domain + [('state', 'not in', ('cancel', 'draft'))]
            paid_domain = domain + [('state', '=', 'posted')]

            if to_date:
                to_pay_domain += [('confirmation_date', '<=', to_date)]
                paid_domain += [('payment_date', '<=', to_date)]

            advance_to_pay_amount = sum(
                rec.advance_payment_group_ids.search(to_pay_domain).mapped(
                    'to_pay_amount'))
            advance_paid_amount = sum(
                rec.advance_payment_group_ids.search(paid_domain).mapped(
                    'payments_amount'))
            rec.advance_to_pay_amount = advance_to_pay_amount
            rec.advance_paid_amount = advance_paid_amount

    @api.multi
    def mass_payment_group_create(self):
        self.ensure_one()
        self = self.with_context(transaction_id=self.id)
        for invoice in self.invoice_ids.filtered(
                lambda r: r.state == 'open'):
            partner = invoice.partner_id
            already_paying = self.payment_group_ids.filtered(
                lambda x: x.state != 'cancel').mapped('to_pay_move_line_ids')
            to_pay_move_lines = (invoice.open_move_line_ids - already_paying)
            # si ya se mandaron a pagar no creamo
            if not to_pay_move_lines:
                continue
            pay_context = {
                'to_pay_move_line_ids': to_pay_move_lines.ids,
                'default_company_id': invoice.company_id.id,
            }
            self.env['account.payment.group'].with_context(
                pay_context).create({
                    'partner_type': 'supplier',
                    'receiptbook_id': self.budget_id.receiptbook_id.id,
                    'expedient_id': self.expedient_id.id,
                    'partner_id': partner.id,
                    'transaction_id': self.id,
                })
        return True

    @api.multi
    @api.depends(
        'preventive_line_ids.preventive_amount',
    )
    def _get_preventive_amount(self):
        for rec in self:
            rec.preventive_amount = sum(rec.mapped(
                'preventive_line_ids.preventive_amount'))

    @api.multi
    @api.depends(
        'preventive_amount',
        'definitive_amount',
    )
    def _get_preventive_balance(self):
        for rec in self:
            _logger.info(
                'Getting preventive balance for transaction_id %s' % rec.id)
            rec.preventive_balance = (
                rec.preventive_amount - rec.definitive_amount)

    @api.multi
    @api.depends(
        'definitive_amount',
        'invoiced_amount',
    )
    def _get_definitive_balance(self):
        for rec in self:
            _logger.info(
                'Getting definitive balance for transaction_id %s' % rec.id)
            rec.definitive_balance = (
                rec.definitive_amount - rec.invoiced_amount)

    @api.multi
    @api.depends(
        'to_pay_amount',
        'invoiced_amount',
    )
    def _get_invoiced_balance(self):
        for rec in self:
            _logger.info(
                'Getting definitive balance for transaction_id %s' % rec.id)
            rec.invoiced_balance = (
                rec.invoiced_amount - rec.to_pay_amount)

    @api.multi
    @api.depends(
        'paid_amount',
        'to_pay_amount',
    )
    def _get_to_pay_balance(self):
        for rec in self:
            _logger.info(
                'Getting definitive balance for transaction_id %s' % rec.id)
            rec.to_pay_balance = (
                rec.to_pay_amount - rec.paid_amount)

    @api.multi
    @api.depends(
        'preventive_line_ids.definitive_amount',
    )
    def _get_definitive_amount(self):
        for rec in self:
            rec.definitive_amount = sum(rec.mapped(
                'preventive_line_ids.definitive_amount'))

    @api.multi
    @api.depends(
        'preventive_line_ids.invoiced_amount',
    )
    def _get_invoiced_amount(self):
        for rec in self:
            rec.invoiced_amount = sum(rec.mapped(
                'preventive_line_ids.invoiced_amount'))

    @api.multi
    @api.depends(
        'preventive_line_ids.to_pay_amount',
    )
    def _get_to_pay_amount(self):
        for rec in self:
            rec.to_pay_amount = sum(rec.mapped(
                'preventive_line_ids.to_pay_amount'))

    @api.multi
    @api.depends(
        'preventive_line_ids.paid_amount',
    )
    def _get_paid_amount(self):
        for rec in self:
            rec.paid_amount = sum(rec.mapped(
                'preventive_line_ids.paid_amount'))

    @api.multi
    def action_cancel_draft(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_open(self):
        self.write({'state': 'open'})
        return True

    @api.multi
    def action_close(self):
        self.check_closure()
        self.write({'state': 'closed'})
        return True

    @api.multi
    @api.constrains('state')
    def _check_position_balance_amount(self):
        self.mapped('preventive_line_ids')._check_position_balance_amount()

    @api.multi
    def check_closure(self):
        """
        Check preventive lines
        """
        for rec in self:
            if not rec.preventive_line_ids:
                raise ValidationError(_(
                    'To close a transaction there must be at least one'
                    ' preventive line'))

            for line in rec.preventive_line_ids:
                # Usamos float_is_zero por porisbles errores de redondeo
                for field in [
                        'definitive_amount', 'invoiced_amount',
                        'to_pay_amount', 'paid_amount']:
                    if not float_is_zero(
                            (line.preventive_amount - line[field]),
                            precision_rounding=rec.currency_id.rounding):
                        raise ValidationError(_(
                            'To close a transaction, Preventive, Definitive, '
                            'Invoiced, To Pay and Paid amount must be the '
                            'same for each line'))

            # Check advance transactions
            if rec.type_id.with_advance_payment:
                if not float_is_zero(
                        rec.advance_to_return_amount,
                        precision_rounding=rec.currency_id.rounding):
                    raise ValidationError(_(
                        'To close a transaction to return amount must be 0!\n'
                        '* To return amount = advance paid amount - '
                        'invoiced amount\n'
                        '(%s = %s - %s)' % (
                            rec.advance_to_return_amount,
                            rec.advance_paid_amount,
                            rec.invoiced_amount)))

# Constraints
    @api.multi
    @api.constrains(
        'preventive_amount',
        'type_id',
        'expedient_id')
    def _check_transaction_type(self):
        # solo controlamos si hay lineas preventivas
        for rec in self:
            if rec.preventive_line_ids and rec.type_id.with_amount_restriction:
                rest = rec.env[
                    'public_budget.transaction_type_amo_rest'].search(
                    [('transaction_type_id', '=', rec.type_id.id),
                     ('date', '<=', rec.expedient_id.issue_date)],
                    order='date desc', limit=1)
                if rest:
                    if (
                        (rec.company_id.currency_id.round(
                            rest.to_amount - rec.preventive_amount) < 0) or
                        (rec.company_id.currency_id.round(
                            rest.from_amount - rec.preventive_amount) > 0)):
                        raise ValidationError(_(
                            "Preventive Total, Type and Date are not "
                            "compatible with Transaction Amount Restrictions"))

    @api.multi
    def action_new_payment_group(self):
        '''
        This function returns an action that display a new payment group.
        We dont use action on view because it will open on tree view
        '''
        self.ensure_one()
        action = self.env['ir.model.data'].xmlid_to_object(
            'account_payment_group.action_account_payments_group_payable')

        if not action:
            return False

        res = action.read()[0]

        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'action_account_payments_group_payable.'
            'view_account_payment_group_form')
        res['views'] = [(form_view_id, 'form')]

        partner_id = self.partner_id

        res['context'] = {
            'default_transaction_id': self.id,
            'default_partner_id': partner_id and partner_id.id or False,
            'default_partner_type': 'supplier',
        }
        return res

    @api.multi
    def copy(self, default=None):
        res = super(BudgetTransaction, self).copy(default)
        attachments = self.env['ir.attachment'].search(
            [('res_model', '=', 'public_budget.transaction'),
             ('res_id', '=', self.id)])
        for att in attachments:
            att.copy(default={
                'res_id': res.id,
                'name': att.name,
            })
        return res

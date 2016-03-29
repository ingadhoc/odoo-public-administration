# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from datetime import date
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class PublicBudgetSubsidy(models.Model):

    _name = 'public_budget.subsidy'
    _inherits = {
        'public_budget.transaction': 'transaction_id',
    }

    @api.model
    def get_type(self):
        transaction_type = self.env['public_budget.transaction_type'].search(
            [('subsidy', '=', True)], limit=1)
        if not transaction_type:
            raise Warning(
                'No Se encontró ningún tipo de transacción del tipo subsidio')
        return transaction_type

    @api.model
    def create(self, vals):
        return super(PublicBudgetSubsidy, self.with_context(
            default_type_id=self.get_type().id)).create(vals)

    transaction_id = fields.Many2one(
        'public_budget.transaction',
        required=True,
        ondelete='cascade',
        auto_join=True
        )
    # expedient_id = fields.Many2one(
    #     'Expediente Administrativo de Solicitud',
    #     )
    parliamentary_resolution_date = fields.Date(
        'Fecha de Resolución Parlamentaria',
        )
    parliamentary_expedient = fields.Char(
        'Expediente Parlamentario',
        )
    charge_date = fields.Date(
        compute='get_charge_date',
        string='Fecha del Cargo',
        )
    dispositional_order = fields.Char(
        'Orden de disposición',
        readonly=True,
        )
    accountability_state = fields.Selection([
        ('charge_made', 'Cargo Efectuado'),
        ('rendition_presented', 'Rendición Presentada'),
        ('rendition_approved', 'Rendición Aprobada'),
        ],
        'Estado de la Rendición',
        )
    accountability_overcome = fields.Boolean(
        compute='_get_accountability_expiry_date',
        search='search_accountability_overcome',
        string='Rendición Vencida?',
        )
    accountability_expiry_date = fields.Date(
        compute='_get_accountability_expiry_date',
        string='Vencimiento de Rendición ',
        help='Fecha de vencimiento de presentación de rendición',
        )
    accountability_administrative_expedient_id = fields.Many2one(
        'public_budget.expedient',
        'Expediente Administrativo de Rendición',
        help='Expediente Administrativo de Rendición de Subsidio',
        )
    rendition_ids = fields.One2many(
        'public_budget.subsidy.rendition',
        'subsidy_id',
        'Renditions',
        )
    claim_ids = fields.One2many(
        'public_budget.subsidy.claim',
        'subsidy_id',
        'Claims',
        )
    destination = fields.Char(
        )
    amount = fields.Float(
        string='Amount',
        required=True,
        digits=dp.get_precision('Account'),
        # states={'closed': [('readonly', True)]},
        )
    rendition_amount = fields.Float(
        'Monto Rendido',
        compute='get_amounts',
        store=True,
        )
    approved_amount = fields.Float(
        'Monto Aprobado',
        compute='get_amounts',
        store=True,
        )
    pending_amount = fields.Float(
        'Monto Pendiente',
        compute='get_amounts',
        store=True,
        )

    @api.one
    @api.depends(
        'rendition_ids.rendition_amount',
        'rendition_ids.approved_amount',
        )
    def get_amounts(self):
        rendition_amount = sum(
            self.rendition_ids.mapped('rendition_amount'))
        approved_amount = sum(
            self.rendition_ids.mapped('approved_amount'))
        self.approved_amount = approved_amount
        self.rendition_amount = rendition_amount
        self.pending_amount = rendition_amount - approved_amount

    @api.model
    def search_accountability_overcome(self, operator, value):
        # 30 dias para atras, solo hábiles
        to_date = date.today()
        business_days_to_add = 30
        while business_days_to_add > 0:
            to_date = to_date + relativedelta(days=-1)
            weekday = to_date.weekday()
            if weekday >= 5:    # sunday = 6
                continue
            # if to_date in holidays:
            #     continue
            business_days_to_add -= 1

        subsidy_transactions = self.search([]).mapped('transaction_id')
        overcome_checks = self.env['account.check'].search([
            ('voucher_id.transaction_id', 'in', subsidy_transactions.ids),
            ('handed_date', '<', fields.Date.to_string(to_date)),
            ], limit=1)

        transaction_ids = overcome_checks.mapped(
            'voucher_id.transaction_id.id')

        # TODO check that value should be True
        if operator == '=':
            operator = 'in'
        elif operator == '!=':
            operator = 'not in'
        else:
            return []
        return [('transaction_id', 'in', transaction_ids)]

    @api.one
    def _get_accountability_expiry_date(self):
        if self.charge_date:
            expiry_date = fields.Date.from_string(self.charge_date)
            business_days_to_add = 30
            while business_days_to_add > 0:
                expiry_date = expiry_date + relativedelta(days=+1)
                weekday = expiry_date.weekday()
                if weekday >= 5:    # sunday = 6
                    continue
                # if to_date in holidays:
                #     continue
                business_days_to_add -= 1
            # TODO chequear que no hace falta convertir
            self.accountability_expiry_date = fields.Date.to_string(
                expiry_date)
            print '(date.today() - expiry_date)', (date.today() - expiry_date)
            if date.today() > expiry_date:
                self.accountability_overcome = True

    @api.onchange('expedient_id', 'partner_id')
    def set_subsidy_name(self):
        self.name = '%s - %s' % (
            self.expedient_id.number or '', self.partner_id.name or '')

    @api.one
    def get_charge_date(self):
        # issued_checks = self.advance_voucher_ids.mapped('issued_check_ids')
        last_check = self.env['account.check'].search([
            ('voucher_id.transaction_id', '=', self.transaction_id.id),
            ], order='handed_date desc', limit=1)
        self.charge_date = last_check.handed_date

# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
# from datetime import date
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
    cargo_date = fields.Date(
        compute='get_cargo_data',
        string='Fecha del Cargo',
    )
    dispositional_order = fields.Char(
        'Orden de disposición',
        readonly=True,
    )
    accountability_state = fields.Selection([
        ('pending', 'Cargos Pendientes'),
        ('approved', 'Aprobada'),
    ],
        'Estado de la Rendición',
        compute='get_state',
        store=True,
    )
    # accountability_state = fields.Selection([
    #     ('charge_made', 'Cargo Efectuado'),
    #     ('rendition_presented', 'Rendición Presentada'),
    #     ('rendition_approved', 'Rendición Aprobada'),
    # ],
    #     'Estado de la Rendición',
    # )
    accountability_expiry_date = fields.Date(
        compute='get_cargo_data',
        string='Vencimiento de Rendición ',
        help='Fecha de vencimiento de presentación de rendición',
        store=True,
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
    cargo_amount = fields.Float(
        'Cargos',
        help='Cargos Efectuados',
        compute='get_cargo_data',
        store=True,
    )
    pendientes_rendicion_amount = fields.Float(
        'Pendiente Rendición',
        help='Cargos Pendientes de Rendición',
        compute='get_cargo_data',
        store=True,
    )
    pendientes_aprobacion_amount = fields.Float(
        'Pendiente Aprobación',
        help='Cargos Pendientes de Aprobación',
        compute='get_cargo_data',
        store=True,
    )
    rendido_amount = fields.Float(
        'Rendido',
        help='Rendiciones Presentadas',
        compute='get_amounts',
        store=True,
    )
    aprobado_amount = fields.Float(
        'Aprobado',
        help='Rendiciones Aprobadas',
        compute='get_amounts',
        store=True,
    )
    revision_amount = fields.Float(
        'En Revisión',
        help='Rendiciones presentadas en Revisión',
        compute='get_amounts',
        store=True,
    )

    @api.one
    @api.depends(
        'rendition_ids.rendition_amount',
        'rendition_ids.approved_amount',
    )
    def get_amounts(self):
        rendido_amount = sum(
            self.rendition_ids.mapped('rendition_amount'))
        aprobado_amount = sum(
            self.rendition_ids.mapped('approved_amount'))
        self.aprobado_amount = aprobado_amount
        self.rendido_amount = rendido_amount
        self.revision_amount = rendido_amount - aprobado_amount

    @api.onchange('expedient_id', 'partner_id')
    def set_subsidy_name(self):
        self.name = '%s - %s' % (
            self.expedient_id.number or '', self.partner_id.name or '')

    @api.one
    @api.depends(
        'pendientes_aprobacion_amount',
    )
    def get_state(self):
        if self.pendientes_aprobacion_amount:
            accountability_state = 'pending'
        else:
            accountability_state = 'approved'
        self.accountability_state = accountability_state

    @api.one
    @api.depends(
        'rendido_amount',
        'aprobado_amount',
        'voucher_ids.cargo_date',
        'voucher_ids.cargo_amount',
        # TODO chequear si hace falta esto o no
        'advance_voucher_ids.cargo_date',
        'advance_voucher_ids.cargo_amount',
    )
    def get_cargo_data(self):
        vouchers = self.voucher_ids + self.advance_voucher_ids
        cargo_amount = sum(vouchers.mapped('cargo_amount'))
        cargo_date = vouchers.search([
            ('id', 'in', vouchers.ids),
            ('cargo_date', '!=', False),
        ], order='cargo_date desc', limit=1).cargo_date

        expiry_date = False
        if cargo_date:
            expiry_date = fields.Date.from_string(cargo_date)
            # TODO, parametrizable?
            business_days_to_add = 30
            while business_days_to_add > 0:
                expiry_date = expiry_date + relativedelta(days=+1)
                weekday = expiry_date.weekday()
                if weekday >= 5:    # sunday = 6
                    continue
                # if to_date in holidays:
                #     continue
                business_days_to_add -= 1
        self.cargo_date = cargo_date
        self.accountability_expiry_date = fields.Date.to_string(
            expiry_date)
        self.cargo_amount = cargo_amount
        self.pendientes_rendicion_amount = (
            cargo_amount - self.rendido_amount)
        self.pendientes_aprobacion_amount = (
            cargo_amount - self.aprobado_amount)

# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from datetime import date
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
    request_administrative_expedient_id = fields.Many2one(
        'public_budget.expedient',
        'Expediente Administrativo de Solicitud',
        help='Expediente Administrativo de Solicitud de Subsidio',
        )
    parliamentary_resolution_date = fields.Date(
        'Fecha de Resolución Parlamentaria',
        )
    parliamentary_expedient_id = fields.Many2one(
        'public_budget.expedient',
        'Expediente Parlamentario',
        )
    check_handed_date = fields.Date(
        compute='get_check_handed_date',
        string='Fecha de Entrega de Cheque',
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

    @api.model
    def search_accountability_overcome(self, operator, value):
        to_date = date.today() + relativedelta(days=-30)
        overcome_checks = self.env['account.check'].search([
            ('voucher_id.transaction_id', '=', self.transaction_id.id),
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
        if self.check_handed_date:
            base_date = fields.Date.from_string(self.check_handed_date)
            expiry_date = base_date + relativedelta(days=+30)
            # TODO chequear que no hace falta convertir
            self.accountability_expiry_date = fields.Date.to_string(
                expiry_date)
            print '(date.today() - expiry_date)', (date.today() - expiry_date)
            if (date.today() - expiry_date) < 0:
                self.accountability_overcome = True

    @api.one
    def get_check_handed_date(self):
        # issued_checks = self.advance_voucher_ids.mapped('issued_check_ids')
        last_check = self.env['account.check'].search([
            ('voucher_id.transaction_id', '=', self.transaction_id.id),
            ], order='handed_date desc', limit=1)
        self.check_handed_date = last_check.handed_date

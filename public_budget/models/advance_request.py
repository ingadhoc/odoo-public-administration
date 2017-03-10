# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AdvanceRequest(models.Model):
    """
    This model is to deal with advance request made by employees
    """

    _name = 'public_budget.advance_request'
    _description = 'Advance Requests'
    _order = 'date desc'

    _states_ = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        # ('done', 'Done'),
        ('cancel', 'Cancel'),
    ]

    name = fields.Char(
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'public_budget.advance_request')
    )
    date = fields.Date(
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today,
        copy=False,
    )
    approval_date = fields.Date(
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    confirmation_date = fields.Date(
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        readonly=True,
        default=lambda self: self.env.user,
        states={'draft': [('readonly', False)]},
    )
    type_id = fields.Many2one(
        'public_budget.advance_request_type',
        string='Type',
        required=True,
        readonly=True,
        domain="[('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        _states_,
        'State',
        default='draft',
        readonly=True,
    )
    advance_request_line_ids = fields.One2many(
        'public_budget.advance_request_line',
        'advance_request_id',
        string='Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # TODO implementar y migrar datos
    # voucher_ids = fields.One2many(
    #     'account.voucher',
    #     'advance_request_id',
    #     # compute='get_vouchers',
    #     # inverse='dummy_inverse',
    #     string='Vouchers',
    # )

    @api.multi
    def action_approve(self):
        for record in self:
            record.state = 'approved'
            if not record.approval_date:
                record.approval_date = fields.Datetime.now()
        return True

    @api.multi
    def action_confirm(self):
        for record in self:
            record.create_voucher()
            record.state = 'confirmed'
            if not record.confirmation_date:
                record.confirmation_date = fields.Datetime.now()
        return True

    @api.multi
    def create_voucher(self):
        self.ensure_one()
        vouchers = self.env['account.voucher']
        amount = sum(self.advance_request_line_ids.mapped('approved_amount'))
        journal = self.env['account.journal'].search([
            ('company_id', '=', self.company_id.id),
            ('type', 'in', ('cash', 'bank'))], limit=1)
        if not journal:
            raise ValidationError(_(
                'No bank or cash journal found for company "%s"') % (
                self.company_id.name))
        partner = self.type_id.general_return_partner_id
        currency = journal.currency or self.company_id.currency_id
        voucher_data = vouchers.onchange_partner_id(
            partner.id, journal.id, 0.0,
            currency.id, 'payment', False)
        voucher_vals = {
            'type': 'payment',
            'partner_id': partner.id,
            'journal_id': journal.id,
            'advance_amount': amount,
            'advance_request_id': self.id,
            'account_id': voucher_data['value'].get('account_id', False),
        }
        return vouchers.create(voucher_vals)

    @api.multi
    @api.constrains('state', 'advance_request_line_ids')
    def check_amounts(self):
        for rec in self:
            if rec.state == 'approved':
                cero_lines = rec.advance_request_line_ids.filtered(
                    lambda x: not x.approved_amount)
                if cero_lines:
                    raise ValidationError(_(
                        'You can not approve a request with lines without '
                        'approved amount.'))

    @api.multi
    @api.constrains('type_id', 'company_id')
    def check_type_company(self):
        for rec in self:
            if rec.type_id.company_id != rec.company_id:
                raise ValidationError(_(
                    'Company must be the same as Type Company!'))

    @api.multi
    def action_cancel(self):
        for request in self:
            open_vouchers = self.voucher_ids.filtered(
                lambda x: x.state not in ['draft', 'cancel'])
            if open_vouchers:
                raise ValidationError(_(
                    'You can nopt cancel an advance request with vouchers in '
                    'other state than "cancel" or "draft".\n'
                    ' * Request id: %i\n'
                    ' * Voucher ids: %s'
                ) % (request.id, open_vouchers.ids))
            self.voucher_ids.unlink()
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_cancel_draft(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'draft'})
        return True

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise ValidationError(_(
                    'You can not delete if record is not on "draft" or '
                    '"cancel" state!'))
        return super(AdvanceRequest, self).unlink()

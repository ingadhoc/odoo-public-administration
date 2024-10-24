from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
        required=True,
        readonly=True,
        default=lambda self: self.env.user,
        states={'draft': [('readonly', False)]},
    )
    type_id = fields.Many2one(
        'public_budget.advance_request_type',
        required=True,
        readonly=True,
        domain="[('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        _states_,
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
    payment_group_ids = fields.One2many(
        'account.payment.group',
        'advance_request_id',
        string='Payment Orders',
    )
    approval_user = fields.Many2one('res.users', string='Aprobado por')

    def action_approve(self):
        for record in self:
            record.state = 'approved'
            record.approval_user = self.env.uid
            if not record.approval_date:
                record.approval_date = fields.Datetime.now()
        return True

    def action_confirm(self):
        for record in self:
            record.create_payment_group()
            record.state = 'confirmed'
            if not record.confirmation_date:
                record.confirmation_date = fields.Datetime.now()
        return True

    def create_payment_group(self):
        self.ensure_one()
        partner = self.type_id.general_return_partner_id
        amount = sum(self.advance_request_line_ids.mapped('approved_amount'))
        res = self.payment_group_ids.create({
            'partner_id': partner.id,
            'unreconciled_amount': amount,
            'advance_request_id': self.id,
            'partner_type': 'supplier',
        })
        res.remove_all()
        res.to_pay_amount = amount
        return res

    @api.constrains('state', 'advance_request_line_ids')
    def check_amounts(self):
        for rec in self.filtered(lambda x: x.state == 'approved'):
            cero_lines = rec.advance_request_line_ids.filtered(
                lambda x: not x.approved_amount)
            if cero_lines:
                raise ValidationError(_(
                    'You can not approve a request with lines without '
                    'approved amount.'))

    @api.constrains('type_id', 'company_id')
    def check_type_company(self):
        if self.filtered(lambda x: x.type_id.company_id != x.company_id):
            raise ValidationError(_(
                'Company must be the same as Type Company!'))

    def action_cancel(self):
        for rec in self:
            open_payments = rec.payment_group_ids.filtered(
                lambda x: x.state != 'cancel')
            if open_payments:
                raise ValidationError(_(
                    "You can't cancel an advance request with payment order "
                    "in other state than 'cancel'."))
        self.write({'state': 'cancel'})
        return True

    def action_cancel_draft(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'draft'})
        return True

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise ValidationError(_(
                    'You can not delete if record is not on "draft" or '
                    '"cancel" state!'))
        return super().unlink()

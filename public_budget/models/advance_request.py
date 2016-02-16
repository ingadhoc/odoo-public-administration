# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class advance_request(models.Model):
    """"""

    _name = 'public_budget.advance_request'
    _description = 'advance_request'

    _states_ = [
        # State machine: untitle
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        # ('done', 'Done'),
        ('cancel', 'Cancel'),
    ]

    _order = "date desc"

    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'public_budget.advance_request')
        )
    date = fields.Date(
        string='Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today
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
    voucher_ids = fields.One2many(
        'account.voucher',
        'advance_request_id',
        # compute='get_vouchers',
        # inverse='dummy_inverse',
        string='Vouchers',
        )

    # @api.one
    # def dummy_inverse(self):
    #     """
    #     Dummy Inverse function so that we can edit vouchers and save changes
    #     """
    #     return True

    # @api.one
    # @api.depends('advance_request_line_ids.voucher_id')
    # def get_vouchers(self):
    #     self.voucher_ids = self.mapped(
    #         'advance_request_line_ids.voucher_id')

    @api.multi
    def action_approve(self):
        self.write({'state': 'approved'})
        return True

    @api.multi
    def action_confirm(self):
        for request in self:
            # request.advance_request_line_ids.create_voucher()
            self.create_voucher()
        self.write({'state': 'confirmed'})
        return True

    @api.one
    def create_voucher(self):
        vouchers = self.env['account.voucher']
        amount = sum(self.advance_request_line_ids.mapped('approved_amount'))
        journal = self.env['account.journal'].search([
            ('company_id', '=', self.company_id.id),
            ('type', 'in', ('cash', 'bank'))], limit=1)
        if not journal:
            raise Warning(_(
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

    @api.one
    @api.constrains('state', 'advance_request_line_ids')
    def check_amounts(self):
        if self.state == 'approved':
            cero_lines = self.advance_request_line_ids.filtered(
                lambda x: not x.approved_amount)
            if cero_lines:
                raise Warning(_(
                    'You can not approve a request with lines without '
                    'approved amount.'))

    @api.one
    @api.constrains('type_id', 'company_id')
    def check_type_company(self):
        if self.type_id.company_id != self.company_id:
            raise Warning(_(
                'Company must be the same as Type Company!'))

    @api.multi
    def action_cancel(self):
        for request in self:
            open_vouchers = self.voucher_ids.filtered(
                    lambda x: x.state not in ['draft', 'cancel'])
            if open_vouchers:
                raise Warning(_(
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

    @api.one
    def unlink(self):
        if self.state not in ['draft', 'cancel']:
            raise Warning(_(
                'You can not delete if record is not on "draft" or "cancel" '
                'state!'))
        return super(advance_request, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

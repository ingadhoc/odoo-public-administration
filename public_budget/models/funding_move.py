# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class FundingMove(models.Model):

    _name = 'public_budget.funding_move'
    _description = 'Funding Move'

    _states_ = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancel'),
    ]

    date = fields.Date(
        required=True,
        default=fields.Date.context_today
    )
    name = fields.Char(
        required=True
    )
    type = fields.Selection(
        [(u'request', u'Request'), (u'refund', u'Refund')],
        required=True,
        default='request'
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        domain=[('type', 'in', ('cash', 'bank'))]
    )
    amount = fields.Monetary(
        required=True,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False
    )
    state = fields.Selection(
        _states_,
        default='draft',
    )
    budget_id = fields.Many2one(
        'public_budget.budget',
        ondelete='cascade',
        string='Budget',
        required=True,
        domain=[('state', '=', 'open')]
    )
    currency_id = fields.Many2one(
        related='budget_id.currency_id',
        readonly=True,
    )
    income_account_id = fields.Many2one(
        'account.account',
        string='Income Account',
        help='If no income account is configured, then income default income '
        'account configured on budget is going to be used.',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('internal_type', '=', 'other'), "
        # no me gasto en este filtro porque no usan multicompany y deberia
        # llevarla
        # "('company_id', '=', company_id), "
        "('deprecated', '=', False)]",
    )
    budget_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Budget Position',
        context={
            'default_type': 'normal', 'default_budget_assignment_allowed': 1},
        domain=[('budget_assignment_allowed', '=', True)]
    )

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
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft'):
                raise ValidationError(
                    _('The funding move must be in draft state for unlink !'))
        return super(FundingMove, self).unlink()

    @api.multi
    @api.constrains('state')
    def _check_cancel(self):
        for rec in self:
            if rec.state == 'cancel' and self.move_id:
                raise ValidationError(_(
                    "You can not cancel a Funding Move that has a related "
                    "Account Move. Delete it first"))

    @api.multi
    def action_confirm(self):
        for rec in self:
            income_account = rec.income_account_id or \
                rec.budget_id.income_account_id
            if not income_account:
                raise ValidationError(_(
                    'No Income account defined on the funding move or the '
                    'budget'))
            if rec.type == 'refund':
                account_id = rec.journal_id.default_debit_account_id.id
                debit = 0.0
                credit = rec.amount
            else:
                account_id = rec.journal_id.default_credit_account_id.id
                credit = 0.0
                debit = rec.amount

            move_line1 = {
                'name': rec.name[:64],
                'date': rec.date,
                'debit': debit,
                'credit': credit,
                'account_id': account_id,
            }
            move_line2 = {
                'name': rec.name[:64],
                'date': rec.date,
                'debit': credit,
                'credit': debit,
                'account_id': income_account.id,
            }

            move_vals = {
                'ref': rec.name,
                'line_ids': [(0, 0, move_line2), (0, 0, move_line1)],
                'journal_id': rec.journal_id.id,
                'date': rec.date,
            }
            move = rec.env['account.move'].create(move_vals)
            rec.write({'move_id': move.id, 'state': 'confirmed'})
            move.post()

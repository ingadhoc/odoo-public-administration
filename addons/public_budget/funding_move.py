# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class funding_move(models.Model):
    """"""

    _name = 'public_budget.funding_move'
    _description = 'funding_move'

    _states_ = [
        # State machine: untitle
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancel'),
    ]

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today
        )
    name = fields.Char(
        string='Name',
        required=True
        )
    type = fields.Selection(
        [(u'request', u'Request'), (u'refund', u'Refund')],
        string='Type',
        required=True,
        default='request'
        )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        domain=[('type', 'in', ('cash', 'bank'))]
        )
    amount = fields.Float(
        string='Amount',
        required=True
        )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False
        )
    state = fields.Selection(
        _states_,
        'State',
        default='draft',
        )
    budget_id = fields.Many2one(
        'public_budget.budget',
        ondelete='cascade',
        string='Budget',
        required=True,
        domain=[('state', '=', 'open')]
        )

    @api.multi
    def action_cancel_draft(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

    @api.one
    def unlink(self):
        if self.state not in ('draft'):
            raise Warning(
                _('The funding move must be in draft state for unlink !'))
        return super(funding_move, self).unlink()

    @api.one
    @api.constrains('state')
    def _check_cancel(self):
        if self.state == 'cancel' and self.move_id:
            raise Warning(
                _("You can not cancel a Funding Move that has a related \
                Account Move. Delete it first"))

    @api.one
    def action_confirm(self):
        if self.type == 'refund':
            account_id = self.journal_id.default_debit_account_id.id
            debit = 0.0
            credit = self.amount
        else:
            account_id = self.journal_id.default_credit_account_id.id
            credit = 0.0
            debit = self.amount

        move_line1 = {
            'name': self.name[:64],
            'date': self.date,
            'debit': debit,
            'credit': credit,
            'account_id': account_id,
        }
        move_line2 = {
            'name': self.name[:64],
            'date': self.date,
            'debit': credit,
            'credit': debit,
            'account_id': self.budget_id.income_account_id.id,
        }

        period = self.env['account.period'].find(self.date)[:1]

        move_vals = {
            'ref': self.name,
            'line_id': [(0, 0, move_line2), (0, 0, move_line1)],
            'journal_id': self.journal_id.id,
            'date': self.date,
            'period_id': period.id,
        }
        move = self.env['account.move'].create(move_vals)
        self.write({'move_id': move.id, 'state': 'confirmed'})
        move.post()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

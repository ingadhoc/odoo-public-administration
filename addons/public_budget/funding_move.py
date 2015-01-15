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

    _constraints = [
    ]

    @api.multi
    def action_cancel_draft(self):
        # go from canceled state to draft state
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

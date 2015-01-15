# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class advance_return(models.Model):
    """"""

    _name = 'public_budget.advance_return'
    _description = 'advance_return'

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
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True
        )
    move_id = fields.Many2one(
        'account.move',
        string='Move',
        readonly=True
        )
    state = fields.Selection(
        _states_,
        'State',
        default='draft',
        )
    transaction_id = fields.Many2one(
        'public_budget.transaction',
        ondelete='cascade',
        string='transaction_id',
        required=True
        )
    return_line_ids = fields.One2many(
        'public_budget.advance_return_line',
        'advance_return_id',
        string='return_line_ids'
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

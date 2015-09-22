# -*- coding: utf-8 -*-
from openerp import models, fields, api


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

    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
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
        states={'draft': [('readonly', False)]},
        )
    move_id = fields.Many2one(
        'account.move',
        string='Move',
        readonly=True,
        )
    state = fields.Selection(
        _states_,
        'State',
        default='draft',
        readonly=True,
        )
    return_line_ids = fields.One2many(
        'public_budget.advance_return_line',
        'advance_return_id',
        string='Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
        )

    @api.multi
    def action_cancel_draft(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

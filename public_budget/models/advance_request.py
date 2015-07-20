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
    state = fields.Selection(
        _states_,
        'State',
        default='draft',
        )
    advance_request_line_ids = fields.One2many(
        'public_budget.advance_request_line',
        'advance_request_id',
        string='advance_request_line_ids'
        )

    @api.multi
    def action_cancel_draft(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

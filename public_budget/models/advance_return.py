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
            'public_budget.advance_return')
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
    def action_confirm(self):
        for record in self:
            move_vals = {
                'das': 'sada',
            }
            move = self.move_id.create(move_vals)
            self.move_id = move.id
        self.write({'state': 'confirmed'})
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.one
    @api.constrains('type_id', 'company_id')
    def check_type_company(self):
        if self.type_id.company_id != self.company_id:
            raise Warning(_(
                'Company must be the same as Type Company!'))

    @api.one
    @api.constrains('state', 'return_line_ids')
    def check_amounts(self):
        if self.state == 'approved':
            cero_lines = self.return_line_ids.filtered(
                lambda x: not x.returned_amount)
            if cero_lines:
                raise Warning(_(
                    'You can not approve a return with lines without '
                    'returned amount.'))

    @api.multi
    def action_cancel_draft(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

    @api.one
    def unlink(self):
        if self.state not in ['draft', 'cancel']:
            raise Warning(_(
                'You can not delete if record is not on "draft" or "cancel" '
                'state!'))
        return super(advance_return, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

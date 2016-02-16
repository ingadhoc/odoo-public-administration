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
    confirmation_date = fields.Date(
        string='Fecha de Confirmación',
        readonly=True,
        states={'draft': [('readonly', False)]},
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
    def get_move_vals(self):
        self.ensure_one()
        return_partner = self.type_id.general_return_partner_id
        lines_vals = []

        total_returned_amount = sum(
            self.return_line_ids.mapped('returned_amount'))
        lines_vals.append(
            (0, 0, {
                'partner_id': return_partner.id,
                'credit': total_returned_amount,
                'debit': 0.0,
                'account_id': self.type_id.account_id.id,
                'name': self.name,
                }))
        # old method to add a line for each return, now they want everyhing
        # on one partner
        # total_returned_amount = 0.0
        # for line in self.return_line_ids:
        #     total_returned_amount += line.returned_amount
        #     lines_vals.append(
        #         (0, 0, {
        #             'partner_id': line.employee_id.id,
        #             'credit': line.returned_amount,
        #             'debit': 0.0,
        #             'account_id': self.type_id.account_id.id,
        #             'name': self.name,
        #             }))
        journal = self.type_id.return_journal_id
        ref = journal.sequence_id._next()
        lines_vals.append(
            (0, 0, {
                'partner_id': return_partner.id,
                'debit': total_returned_amount,
                'credit': 0.0,
                'account_id': return_partner.property_account_payable.id,
                'name': self.name,
                }))

        return {
            'line_id': lines_vals,
            'ref': ref,
            'name': self.name,
            'journal_id': journal.id,
        }

    @api.multi
    def action_confirm(self):
        for record in self:
            move_vals = record.get_move_vals()
            move = self.move_id.create(move_vals)
            record.write({
                'move_id': move.id,
                'state': 'confirmed',
                })
            if not record.confirmation_date:
                record.confirmation_date = fields.Datetime.now()
        return True

    @api.multi
    def action_cancel(self):
        for record in self:
            if record.move_id:
                raise Warning(_(
                    'You can not cancel a return if there is a move linked!\n'
                    'Please delete it first'))
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

    @api.onchange('type_id')
    def change_type(self):
        self.return_line_ids = False

    @api.multi
    def compute_debtors(self):
        self.ensure_one()
        actual_employees = self.return_line_ids.mapped('employee_id')
        employees = self.env['res.partner'].search([
            ('employee', '=', True),
            ('id', 'not in', actual_employees.ids)])
        line_vals = []
        for employee in employees:
            employee_debt = employee.get_debt_amount(
                advance_return_type=self.type_id)
            if employee_debt:
                line_vals.append((0, False, {
                    'employee_id': employee.id,
                    'returned_amount': employee_debt,
                    }))
        self.return_line_ids = line_vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

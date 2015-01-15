# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class budget(models.Model):
    """Budget"""

    _name = 'public_budget.budget'
    _description = 'Budget'

    _order = "year desc"

    _states_ = [
        # State machine: untitle
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('pre_closed', 'Pre Closed'),
        ('closed', 'Closed'),
        ('cancel', 'Cancel'),
    ]

    name = fields.Char(
        string='Name',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
        )
    year = fields.Integer(
        string='Year',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
        )
    income_account_id = fields.Many2one(
        'account.account',
        string='Income Account',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        context={'default_type': 'other'},
        domain=[('type', '=', 'other'), ('user_type.report_type', 'in', ['income'])]
        )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expedient',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
        )
    prec_passive_residue = fields.Float(
        string='Pre Close Passive Residue',
        readonly=True
        )
    prec_total_requested = fields.Float(
        string='Pre Close Total Requested',
        readonly=True
        )
    total_preventive = fields.Float(
        string='Total Preventive',
        compute='_get_totals'
        )
    total_authorized = fields.Float(
        string='Total Authorized',
        compute='_get_totals'
        )
    total_requested = fields.Float(
        string='Total Requested',
        compute='_get_totals'
        )
    passive_residue = fields.Float(
        string='Total Residue',
        compute='_get_totals'
        )
    budget_position_ids = fields.Many2many(
        relation='public_budget_budget_position_rel',
        comodel_name='public_budget.budget_position',
        string='Budget Positions',
        store=True,
        compute='_get_budget_positions'
        )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env['res.company']._company_default_get('public_budget.budget')
        )
    state = fields.Selection(
        _states_,
        'State',
        default='draft',
        )
    budget_modification_ids = fields.One2many(
        'public_budget.budget_modification',
        'budget_id',
        string='Modifications',
        readonly=True,
        states={'open': [('readonly', False)]},
        domain=[('initial_approval', '=', False)]
        )
    budget_detail_ids = fields.One2many(
        'public_budget.budget_detail',
        'budget_id',
        string='Details',
        readonly=True,
        states={'draft': [('readonly', False)]}
        )
    budget_prec_detail_ids = fields.One2many(
        'public_budget.budget_prec_detail',
        'budget_id',
        string='Pre Close Detail',
        readonly=True
        )
    funding_move_ids = fields.One2many(
        'public_budget.funding_move',
        'budget_id',
        string='Funding Moves',
        readonly=True,
        states={'open': [('readonly', False)], 'pre_closed': [('readonly', False)]},
        context={'from_budget': True}
        )
    preventive_line_ids = fields.One2many(
        'public_budget.preventive_line',
        'budget_id',
        string='Lines'
        )

    _constraints = [
    ]

    @api.one
    def _get_budget_positions(self):
        """"""
        raise NotImplementedError

    @api.one
    def _get_totals(self):
        """"""
        raise NotImplementedError

    @api.multi
    def action_cancel_draft(self):
        # go from canceled state to draft state
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

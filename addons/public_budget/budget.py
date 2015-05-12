# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class budget(models.Model):
    """Budget"""

    _name = 'public_budget.budget'
    _description = 'Budget'

    _order = "fiscalyear_id desc"

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
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        'Fiscal Year',
        required=True,
        states={'done': [('readonly', True)]},
        select=True)
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
        # store=True, #TODO ver si agregamos el store y si es necesario este campo
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
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
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
    transaction_ids = fields.One2many(
        'public_budget.transaction',
        'budget_id',
        string='Transactions'
        )

    _constraints = [
    ]

    @api.one
    @api.depends(
        # TODO borrar comentados si no se necesitan
        # 'budget_detail_ids',
        'budget_detail_ids.budget_position_id',
        # 'transaction_ids',
        'transaction_ids.preventive_line_ids.budget_position_id',
        # 'budget_modification_ids',
        # 'budget_modification_ids.budget_modification_detail_ids',
        'budget_modification_ids.budget_modification_detail_ids.budget_position_id',
    )
    def _get_budget_positions(self):
        """ Definimos por ahora llevar solamente las posiciones que tienen
        admitida la asignacion de presupuesto. 
        La unica diferencia entre los dos metodos es que el segundo lleva ademas
        posiciones que fueron utilizadas en transacciones pero que no tenian
        marcada la opcion de asignacion de presupuesto"""
        budget_positions = self.env['public_budget.budget_position']
        self.budget_position_ids = budget_positions

        modifications = self.env[
            'public_budget.budget_modification_detail'].search(
            [('budget_modification_id.budget_id', '=', self.id)])

        # modifications
        position_ids = [x.budget_position_id.id for x in modifications]
        # initial positions
        position_ids = position_ids + [
            x.budget_position_id.id for x in self.budget_detail_ids]
        # eliminate duplicated
        position_ids = list(set(position_ids))
        # parents positions
        for position in budget_positions.browse(position_ids):
            parents = budget_positions.search(
                [('parent_left', '<', position.parent_left),
                 ('parent_right', '>', position.parent_right)])
            position_ids += parents.ids
        self.budget_position_ids = budget_positions.browse(
            list(set(position_ids))).sorted(key=lambda r: r.parent_left)

        # Torma vieja donde llevabamos padres e hijos de todas las posiciones
        # involucradas en un presupuesto
        # budget_positions = self.env['public_budget.budget_position']
        # self.budget_position_ids = budget_positions

        # modifications = self.env[
        #     'public_budget.budget_modification_detail'].search(
        #     [('budget_modification_id.budget_id', '=', self.id)])

        # # modifications
        # position_ids = [x.budget_position_id.id for x in modifications]
        # # initial positions
        # position_ids = position_ids + [
        #     x.budget_position_id.id for x in self.budget_detail_ids]
        # # transactions positions
        # position_ids = position_ids + [
        #     x.budget_position_id.id for x in self.preventive_line_ids]
        # # eliminate duplicated
        # position_ids = list(set(position_ids))
        # # parents positions
        # for position in budget_positions.browse(position_ids):
        #     parents = budget_positions.search(
        #         [('parent_left', '<', position.parent_left),
        #          ('parent_right', '>', position.parent_right)])
        #     position_ids += parents.ids
        # self.budget_position_ids = budget_positions.browse(
        #     list(set(position_ids)))

    @api.one
    def _get_totals(self):
        total_authorized = sum([x.amount for x in self.with_context(
            budget_id=self.id).budget_position_ids if x.type != 'view'])
        total_preventive = sum(
            [x.preventive_amount for x in self.with_context(
                budget_id=self.id).budget_position_ids if x.type != 'view'])
        total_requested = sum(
            [x.amount for x in self.with_context(
                budget_id=self.id).funding_move_ids if x.type == 'request']) - sum(
            [x.amount for x in self.with_context(
                budget_id=self.id).funding_move_ids if x.type == 'refund'])

        self.total_authorized = total_authorized
        self.total_preventive = total_preventive
        self.total_requested = total_requested

        # Get passive residue
        definitive_lines = self.env['public_budget.definitive_line'].search(
            [('budget_id', '=', self.id)])
        passive_residue = sum([x.residual_amount for x in definitive_lines])
        self.passive_residue = passive_residue

    @api.multi
    def action_cancel_draft(self):
        # go from canceled state to draft state
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

    @api.one
    def action_pre_close(self):
        # Unlink any previous pre close detail
        self.budget_prec_detail_ids.unlink()
        self = self.with_context(budget_id=self.id)

        self.prec_passive_residue = self.passive_residue
        self.prec_total_requested = self.total_requested

        for line in self.budget_position_ids:
            vals = {
                'budget_position_id': line.id,
                'amount': line.amount,
                'draft_amount': line.draft_amount,
                'preventive_amount': line.preventive_amount,
                'definitive_amount': line.definitive_amount,
                'to_pay_amount': line.to_pay_amount,
                'paid_amount': line.paid_amount,
                'balance_amount': line.balance_amount,
                'parent_left': line.parent_left,
                'order_int': line.parent_left,
                'budget_id': self.id,
            }
            self.budget_prec_detail_ids.create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

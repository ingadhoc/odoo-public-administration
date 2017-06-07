# -*- coding: utf-8 -*-
from openerp import models, fields, api


class Budget(models.Model):

    _name = 'public_budget.budget'
    _description = 'Budget'

    # _order = "fiscalyear_id desc"

    _states_ = [
        # State machine: untitle
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('pre_closed', 'Pre Closed'),
        ('closed', 'Closed'),
        ('cancel', 'Cancel'),
    ]

    name = fields.Char(
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )
    # fiscalyear_id = fields.Many2one(
    #     'account.fiscalyear',
    #     'Fiscal Year',
    #     required=True,
    #     states={'draft': [('readonly', False)]},
    #     select=True)
    income_account_id = fields.Many2one(
        'account.account',
        string='Income Account',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        domain="[('internal_type', '=', 'other'), "
        "('company_id', '=', company_id), "
        "('deprecated', '=', False)]",

    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        string='Expedient',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )
    prec_passive_residue = fields.Monetary(
        string='Pre Close Passive Residue',
        readonly=True,
    )
    prec_total_requested = fields.Monetary(
        string='Pre Close Total Requested',
        readonly=True,
    )
    total_preventive = fields.Monetary(
        string='Total Preventivo',
        compute='_compute_totals',
        # store=True,
    )
    total_authorized = fields.Monetary(
        string='Total Autorizado',
        compute='_compute_totals',
        # store=True,
    )
    total_requested = fields.Monetary(
        string='Total Requerido',
        compute='_compute_totals',
        # store=True,
    )
    passive_residue = fields.Monetary(
        string='Total Residuo',
        compute='_compute_totals',
        # store=True,
    )
    parent_budget_position_ids = fields.Many2many(
        comodel_name='public_budget.budget_position',
        string='Budget Positions',
        compute='_compute_budget_positions'
    )
    budget_position_ids = fields.Many2many(
        relation='public_budget_budget_position_rel',
        comodel_name='public_budget.budget_position',
        string='Budget Positions',
        # store=True, #TODO ver si agregamos el store
        compute='_compute_budget_positions'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_compute(
            'public_budget.budget')
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True,
    )
    state = fields.Selection(
        _states_,
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
        states={
            'open': [('readonly', False)],
            'pre_closed': [('readonly', False)]},
        context={'from_budget': True}
    )
    transaction_ids = fields.One2many(
        'public_budget.transaction',
        'budget_id',
        string='Transactions'
    )
    receiptbook_id = fields.Many2one(
        'account.payment.receiptbook',
        'ReceiptBook',
        required=True,
        states={'draft': [('readonly', False)]},
        domain="[('partner_type', '=', 'supplier'), "
        "('company_id', '=', company_id)]",
    )

    @api.one
    @api.depends(
        'budget_detail_ids.budget_position_id',
        'transaction_ids.preventive_line_ids.budget_position_id',
        'budget_modification_ids.budget_modification_detail_ids.'
        'budget_position_id',
    )
    def _compute_budget_positions(self):
        """ Definimos por ahora llevar solamente las posiciones que tienen
        admitida la asignacion de presupuesto.
        """
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
        self.parent_budget_position_ids = self.budget_position_ids.filtered(
            lambda x: not x.parent_id)

    @api.one
    def _compute_totals(self):
        total_authorized = sum([x.amount for x in self.with_context(
            budget_id=self.id).budget_position_ids
            if x.budget_assignment_allowed])
        total_preventive = sum(
            [x.preventive_amount for x in self.with_context(
                budget_id=self.id).budget_position_ids
                if x.budget_assignment_allowed])
        total_requested = sum(
            [x.amount for x in self.with_context(
                budget_id=self.id).funding_move_ids
                if x.type == 'request']) - sum(
                    [x.amount for x in self.with_context(
                        budget_id=self.id).funding_move_ids
                        if x.type == 'refund'])

        self.total_authorized = total_authorized
        self.total_preventive = total_preventive
        self.total_requested = total_requested

        # we use sql instead of orm becuase as this computed fields are not
        # stored, the computation use methods and not stored values
        # Get passive residue
        definitive_lines = self.env['public_budget.definitive_line'].search(
            [('budget_id', '=', self.id)])
        if definitive_lines:
            self._cr.execute(
                'SELECT residual_amount '
                'FROM public_budget_definitive_line '
                'WHERE id IN %s', (tuple(definitive_lines.ids),))
            self.passive_residue = sum([x[0] for x in self._cr.fetchall()])

    @api.multi
    def action_cancel_draft(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_open(self):
        self.write({'state': 'open'})
        return True

    @api.multi
    def action_close(self):
        self.write({'state': 'closed'})
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_pre_close(self):
        # Unlink any previous pre close detail
        for rec in self:
            rec.budget_prec_detail_ids.unlink()
            rec = rec.with_context(budget_id=rec.id)

            rec.prec_passive_residue = rec.passive_residue
            rec.prec_total_requested = rec.total_requested

            for line in rec.budget_position_ids:
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
                    'budget_id': rec.id,
                }
                rec.budget_prec_detail_ids.create(vals)
        self.write({'state': 'pre_closed'})

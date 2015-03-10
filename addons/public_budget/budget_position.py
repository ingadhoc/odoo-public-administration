# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime


class budget_position(models.Model):
    """Budget Position"""

    _name = 'public_budget.budget_position'
    _description = 'Budget Position'
    _parent_order = 'code'
    _parent_store = True

    _order = "parent_left"

    code = fields.Char(
        string='Code',
        required=True
        )
    name = fields.Char(
        string='Name',
        required=True
        )
    type = fields.Selection(
        [(u'normal', u'Normal'), (u'view', u'View')],
        string='Type',
        required=True,
        default='normal'
        )
    budget_assignment_allowed = fields.Boolean(
        string='Budget Assignment Allowed?'
        )
    category_id = fields.Many2one(
        'public_budget.budget_position_category',
        string='Category'
        )
    inventariable = fields.Boolean(
        string='Inventariable?'
        )
    draft_amount = fields.Float(
        string='Draft Amount',
        compute='_get_amounts'
        )
    preventive_amount = fields.Float(
        string='Preventive Amount',
        compute='_get_amounts'
        )
    definitive_amount = fields.Float(
        string='Definitive Amount',
        compute='_get_amounts'
        )
    to_pay_amount = fields.Float(
        string='To Pay Amount',
        compute='_get_amounts'
        )
    paid_amount = fields.Float(
        string='Paid Amount',
        compute='_get_amounts'
        )
    balance_amount = fields.Float(
        string='Balance Amount',
        compute='_get_amounts'
        )
    projected_amount = fields.Float(
        string='Projected Amount',
        compute='_get_amounts'
        )
    projected_avg = fields.Float(
        string='Projected Avg',
        compute='_get_amounts'
        )
    preventive_avg = fields.Float(
        string='Preventive Avg',
        compute='_get_amounts'
        )
    amount = fields.Float(
        string='Amount',
        compute='_get_amounts'
        )
    parent_left = fields.Integer(
        string='Parent Left',
        select=True
        )
    parent_right = fields.Integer(
        string='Parent Right',
        select=True
        )
    available_account_ids = fields.Many2many(
        'account.account',
        'public_budget_budget_position_ids_available_account_ids_rel',
        'budget_position_id',
        'account_id',
        string='Available Accounts'
        )
    child_ids = fields.One2many(
        'public_budget.budget_position',
        'parent_id',
        string='Childs'
        )
    parent_id = fields.Many2one(
        'public_budget.budget_position',
        string='Parent',
        ondelete='cascade',
        context={'default_type':'view'},
        domain=[('type','=','view')]
        )
    budget_detail_ids = fields.One2many(
        'public_budget.budget_detail',
        'budget_position_id',
        string='budget_detail_ids'
        )
    budget_modification_detail_ids = fields.One2many(
        'public_budget.budget_modification_detail',
        'budget_position_id',
        string='budget_modification_detail_ids'
        )
    preventive_line_ids = fields.One2many(
        'public_budget.preventive_line',
        'budget_position_id',
        string='preventive_line_ids'
        )
    assignment_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Assignment Position',
        compute='_get_assignment_position',
        # store=True, # TODO ver si la hacemos store
        )

    _constraints = [
    ]

    @api.one
    def _get_amounts(self):
        """Update the following fields with the related values to the budget
        and the budget position:
        -draft_amount: amount sum on preventive lines in draft state
        -preventive_amount: amount sum on preventive lines not in draft/cancel
        -definitive_amount: amount sum of definitive lines
        -to_pay_amount: amount sum of lines that has a related voucher in draft
        state
        -paid_amount: amount sum of lines that has a related voucher in open
        state
        -balance_amount: diffference between budget position and preventive
        amount
        """
        if self.type == 'view':
            operator = 'child_of'
        if self.type == 'normal':
            operator = '='

        domain = [('budget_position_id', operator, self.id)]

        budget_id = self._context.get('budget_id', False)
        # we add budget_assignment_allowed condition to optimize
        if budget_id and self.budget_assignment_allowed:
            domain.append(('budget_id', '=', budget_id))
            modification_lines = self.env[
                'public_budget.budget_modification_detail'].search([
                ('budget_modification_id.budget_id', '=', budget_id),
                ('budget_position_id', operator, self.id)])
            modification_amounts = [line.amount for line in modification_lines]
            initial_lines = self.env['public_budget.budget_detail'].search([
                ('budget_id', '=', budget_id),
                ('budget_position_id', operator, self.id)])
            initial_amounts = [line.amount for line in initial_lines]
            amount = sum(initial_amounts) + sum(modification_amounts)
        else:
            amount = False

        draft_preventive_lines = self.env[
            'public_budget.preventive_line'].search(
            domain
            )
        active_preventive_lines = self.env[
            'public_budget.preventive_line'].search(
            domain
            )

        draft_amounts = [
            line.preventive_amount
            for line
            in draft_preventive_lines]

        preventive_amount = sum(
            [line.preventive_amount for line in active_preventive_lines])
        self.draft_amount = sum(draft_amounts)
        self.preventive_amount = preventive_amount
        self.definitive_amount = sum(
            [line.definitive_amount for line in active_preventive_lines])
        self.to_pay_amount = sum(
            [line.to_pay_amount for line in active_preventive_lines])
        self.paid_amount = sum(
            [line.paid_amount for line in active_preventive_lines])

        day_of_year = datetime.now().timetuple().tm_yday
        projected_amount = preventive_amount / day_of_year * 365
        self.projected_amount = projected_amount

        projected_avg = amount and \
            projected_amount / amount * 100.0 or 0.0
        self.projected_avg = projected_avg

        preventive_avg = amount and \
            preventive_amount / amount * 100.0 or 0.0
        self.preventive_avg = preventive_avg
        self.amount = amount
        self.balance_amount = self.amount - preventive_amount

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id, "%s - %s" % (rec.code, rec.name)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.one
    @api.constrains('child_ids', 'type', 'parent_id')
    def _check_type(self):
        if self.child_ids and self.type not in ('view'):
            raise Warning(_('You cannot define children to an account with \
                internal type different of "View".'))

    @api.one
    @api.constrains(
        'budget_modification_detail_ids',
        'budget_detail_ids',
        'child_ids',
        'budget_assignment_allowed',
        'parent_id'
    )
    def _check_budget_assignment_allowed(self):
        # Check before seting budget_assignment_allowed false if position used
        if not self.budget_assignment_allowed and (self.budget_modification_detail_ids or self.budget_detail_ids):
            raise Warning(_("You can not set 'Budget Assignment Allowed' to false if budget position is\
                being used in a budget detail or modification."))
        if self.budget_assignment_allowed:
            # Checl no parent has budget allowed
            if len(self.get_parent_assignment_position()) > 1:
                raise Warning(_('In one branch only one budget position can have \
                    Budget Assignment Allowed.'))
            # Checl no children has budget allowed
            else:
                children_allowed = self.search([
                    ('id', 'child_of', self.id),
                    ('id', '!=', self.id),
                    ('budget_assignment_allowed', '=', True)])
                if children_allowed:
                    raise Warning(_(
                        'You can not set position %s to Budget Posistion \
                        Allowed as the child position %s has Allowed.') % (
                        self.name, children_allowed[0].name))

    @api.multi
    def get_parent_assignment_position(self):
        self.ensure_one()
        parents = self.search([
            ('parent_left', '<', self.parent_left),
            ('parent_right', '>', self.parent_right)
            ])
        positions_assignment_allowed = [
            x for x in parents if x.budget_assignment_allowed]
        return positions_assignment_allowed and positions_assignment_allowed[0] or []

    @api.one
    @api.depends(
        'parent_id',
        'child_ids',
        'budget_assignment_allowed',
    )
    def _get_assignment_position(self):
        if self.budget_assignment_allowed:
            assignment_position_id = self
        else:
            assignment_position_id = self.get_parent_assignment_position()
        self.assignment_position_id = assignment_position_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

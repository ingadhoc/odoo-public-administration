# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class BudgetPosition(models.Model):

    _name = 'public_budget.budget_position'
    _description = 'Budget Position'
    _parent_order = 'code'
    _parent_store = True

    _order = "parent_left"

    code = fields.Char(
        required=True
    )
    name = fields.Char(
        required=True
    )
    type = fields.Selection(
        [(u'normal', u'Normal'), (u'view', u'View')],
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
    draft_amount = fields.Monetary(
        compute='_get_amounts',
    )
    preventive_amount = fields.Monetary(
        string='Monto Preventivo',
        compute='_get_amounts',
    )
    definitive_amount = fields.Monetary(
        string='Monto Definitivo',
        compute='_get_amounts',
    )
    to_pay_amount = fields.Monetary(
        string='Monto A Pagar',
        compute='_get_amounts',
    )
    paid_amount = fields.Monetary(
        string='Monto Pagado',
        compute='_get_amounts'
    )
    balance_amount = fields.Monetary(
        string='Saldo',
        compute='_get_amounts',
    )
    projected_amount = fields.Monetary(
        string='Monto Proyectado',
        compute='_get_amounts',
    )
    projected_avg = fields.Monetary(
        string='Projected Avg',
        compute='_get_amounts',
    )
    preventive_avg = fields.Monetary(
        string='Porc. Preventivo',
        compute='_get_amounts',
    )
    amount = fields.Monetary(
        string='Monto',
        compute='_get_amounts',
    )
    parent_left = fields.Integer(
        string='Parent Left',
        select=True
    )
    parent_right = fields.Integer(
        string='Parent Right',
        select=True
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
        context={'default_type': 'view'},
        domain=[('type', '=', 'view')]
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
        string='Preventive Lines'
    )
    assignment_position_id = fields.Many2one(
        'public_budget.budget_position',
        string='Assignment Position',
        compute='_get_assignment_position',
        store=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True,
    )
    default_account_id = fields.Many2one(
        'account.account',
        domain="["
        "('internal_type', '=', 'other'), "
        "('company_id', '=', company_id), "
        "('deprecated', '=', False)]",
        string='Default Account',
        help='Default Account on preventive lines of this position'
    )

    @api.one
    # @api.depends(
    #     'preventive_line_ids.affects_budget',
    #     'preventive_line_ids.transaction_id.state',
    #     'preventive_line_ids.preventive_amount',
    #     'preventive_line_ids.definitive_line_ids.amount',
    #     )
    def _get_amounts(self):
        """Update the following fields with the related values to the budget
        and the budget position:
        -draft_amount: amount sum on preventive lines in draft state
        -preventive_amount: amount sum on preventive lines not in draft/cancel
        -definitive_amount: amount sum of definitive lines
        -to_pay_amount: amount sum of lines that has a related payment in draft
        state
        -paid_amount: amount sum of lines that has a related payment in open
        state
        -balance_amount: diffference between budget position and preventive
        amount
        """
        _logger.info('Getting amounts for budget position %s' % self.name)
        if self.type == 'view':
            operator = 'child_of'
        if self.type == 'normal':
            operator = '='

        domain = [
            ('budget_position_id', operator, self.id),
            # esto podria no ir porque el affects_budget ya tiene en cuetna
            # el estado de la transaccion
            ('transaction_id.state', 'in', ('open', 'closed')),
            ('affects_budget', '=', True),
        ]

        budget_id = self._context.get('budget_id', False)
        to_date = self._context.get('analysis_to_date', False)

        # we check it is a report because if not it will get wrong budget
        # on positions
        if not budget_id and 'aeroo_docs' in self._context:
            budget_id = self._context.get('active_id', False)

        if budget_id:
            domain.append(('budget_id', '=', budget_id))
        if to_date:
            _logger.info('Getting budget amounts with to_date %s' % (
                to_date))
            domain += [('transaction_id.issue_date', '<=', to_date)]

        # we add budget_assignment_allowed condition to optimize
        _logger.info('Getting budget amounts')
        # if budget_id and self.budget_assignment_allowed:
        if budget_id and (self.budget_assignment_allowed or self.child_ids):
            modification_domain = [
                ('budget_modification_id.budget_id', '=', budget_id),
                ('budget_position_id', operator, self.id)]
            if to_date:
                modification_domain += [
                    ('budget_modification_id.date', '<=', to_date)]
            modification_lines = self.env[
                'public_budget.budget_modification_detail'].search(
                    modification_domain)
            modification_amounts = [line.amount for line in modification_lines]
            initial_lines = self.env['public_budget.budget_detail'].search([
                ('budget_id', '=', budget_id),
                ('budget_position_id', operator, self.id)])
            initial_amounts = [line.initial_amount for line in initial_lines]
            amount = sum(initial_amounts) + sum(modification_amounts)
        else:
            amount = False

        # we exclude lines from preventive lines because constraints sometimes
        # consider the line you are checking and sometimes not, so better we
        # exclude that line and compare to that line amount
        excluded_line_id = self._context.get('excluded_line_id', False)
        if excluded_line_id:
            domain.append(('id', '!=', excluded_line_id))

        # we use sql instead of orm becuase as this computed fields are not
        # stored, the computation use methods and not stored values
        _logger.info('Getting budget general amounts')

        draft_preventive_lines = self.env[
            'public_budget.preventive_line'].search(
            domain
        )

        if draft_preventive_lines:
            self._cr.execute(
                'SELECT preventive_amount '
                'FROM public_budget_preventive_line '
                'WHERE id IN %s', (tuple(draft_preventive_lines.ids),))
            self.draft_amount = sum([x[0] for x in self._cr.fetchall()])

        _logger.info('Getting budget general amounts')

        active_preventive_lines = self.env[
            'public_budget.preventive_line'].search(
            domain
        )

        preventive_amount = definitive_amount = to_pay_amount = paid_amount = 0
        if active_preventive_lines:
            # if from_date or to_date we can not use stored value, we should
            # get method value (using computed fields)
            # if from_date or to_date:
            if to_date:
                _logger.info('Getting values from computed fields methods')
                for pl in active_preventive_lines:
                    preventive_amount += pl.preventive_amount
                    definitive_amount += pl.definitive_amount
                    to_pay_amount += pl.to_pay_amount
                    paid_amount += pl.paid_amount
            else:
                _logger.info('Getting values from stored fields')
                self._cr.execute(
                    'SELECT preventive_amount, definitive_amount, '
                    'to_pay_amount, paid_amount '
                    'FROM public_budget_preventive_line '
                    'WHERE id IN %s', (tuple(active_preventive_lines.ids),))
                for r in self._cr.fetchall():
                    preventive_amount += r[0]
                    definitive_amount += r[1]
                    to_pay_amount += r[2]
                    paid_amount += r[3]

        self.preventive_amount = preventive_amount
        self.definitive_amount = definitive_amount
        self.to_pay_amount = to_pay_amount
        self.paid_amount = paid_amount

        # if to_date use it, if not, then use now
        if to_date:
            day_of_year = fields.Datetime.from_string(
                to_date).timetuple().tm_yday
        else:
            day_of_year = datetime.now().timetuple().tm_yday
        projected_amount = preventive_amount / day_of_year * 365
        self.projected_amount = projected_amount

        # if self.budget_assignment_allowed:
        # if self.budget_assignment_allowed or self.child_ids:
        if amount:
            _logger.info('Getting budget assignment amounts')
            # projected_avg = amount and \
            #     projected_amount / amount * 100.0 or 0.0
            # self.projected_avg = projected_avg
            self.projected_avg = projected_amount / amount * 100.0
            self.amount = amount
            # preventive_avg = amount and \
            #     preventive_amount / amount * 100.0 or 0.0
            # self.preventive_avg = preventive_avg
            self.preventive_avg = preventive_amount / amount * 100.0
            self.balance_amount = self.amount - preventive_amount
        _logger.info(
            'Finish getting amounts for budget position %s' % self.name)

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

    @api.multi
    @api.constrains('child_ids', 'type', 'parent_id')
    def _check_type(self):
        for rec in self:
            if rec.child_ids and rec.type not in ('view'):
                raise ValidationError(_(
                    'You cannot define children to an account with '
                    'internal type different of "View".'))

    @api.multi
    @api.constrains(
        'budget_modification_detail_ids',
        'budget_detail_ids',
        'child_ids',
        'budget_assignment_allowed',
        'parent_id'
    )
    def _check_budget_assignment_allowed(self):
        """
        Check before seting budget_assignment_allowed false if position used
        """
        for rec in self:
            if not rec.budget_assignment_allowed and (
                    rec.budget_modification_detail_ids or
                    rec.budget_detail_ids):
                raise ValidationError(_(
                    "You can not set 'Budget Assignment Allowed' to false if "
                    "budget position is being used in a budget detail or "
                    "modification."))
            if rec.budget_assignment_allowed:
                # Check no parent has budget allowed
                if len(rec.get_parent_assignment_position()) >= 1:
                    raise ValidationError(_(
                        'In one branch only one budget position can '
                        'have Budget Assignment Allowed.'))
                # Check no children has budget allowed
                else:
                    children_allowed = rec.search([
                        ('id', 'child_of', rec.id),
                        ('id', '!=', rec.id),
                        ('budget_assignment_allowed', '=', True)])
                    if children_allowed:
                        raise ValidationError(_(
                            'You can not set position %s to Budget Posistion '
                            'Allowed as the child position %s has Allowed.'
                        ) % (rec.name, children_allowed[0].name))

    @api.multi
    def get_parent_assignment_position(self):
        self.ensure_one()
        assignment_allowed = self.env['public_budget.budget_position']
        parent = self.parent_id
        while parent:
            if parent.budget_assignment_allowed:
                assignment_allowed += parent
            parent = parent.parent_id
        return assignment_allowed

    @api.multi
    @api.depends(
        'parent_id',
        'child_ids',
        'budget_assignment_allowed',
    )
    def _get_assignment_position(self):
        for rec in self:
            if rec.budget_assignment_allowed:
                assignment_position = rec
            else:
                assignment_position = rec.get_parent_assignment_position()
            rec.assignment_position_id = assignment_position.id

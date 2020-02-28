from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
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
    )
    inventariable = fields.Boolean(
        string='Inventariable?'
    )
    draft_amount = fields.Monetary(
        compute='_compute_amounts',
        compute_sudo=True,
    )
    preventive_amount = fields.Monetary(
        string='Monto Preventivo',
        compute='_compute_amounts',
        compute_sudo=True,
    )
    definitive_amount = fields.Monetary(
        string='Monto Definitivo',
        compute='_compute_amounts',
        compute_sudo=True,
    )
    to_pay_amount = fields.Monetary(
        string='Monto A Pagar',
        compute='_compute_amounts',
        compute_sudo=True,
    )
    paid_amount = fields.Monetary(
        string='Monto Pagado',
        compute='_compute_amounts',
        compute_sudo=True,
    )
    balance_amount = fields.Monetary(
        string='Saldo',
        compute='_compute_amounts',
        compute_sudo=True,
    )
    projected_amount = fields.Monetary(
        string='Monto Proyectado',
        compute='_compute_amounts',
        compute_sudo=True,
    )
    projected_avg = fields.Monetary(
        string='Projected Avg',
        compute='_compute_amounts',
        compute_sudo=True,
    )
    preventive_avg = fields.Monetary(
        string='Porc. Preventivo',
        compute='_compute_amounts',
        compute_sudo=True,
    )
    amount = fields.Monetary(
        string='Monto',
        compute='_compute_amounts',
        compute_sudo=True,
    )
    parent_left = fields.Integer(
        index=True,
    )
    parent_right = fields.Integer(
        index=True,
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
    )
    budget_modification_detail_ids = fields.One2many(
        'public_budget.budget_modification_detail',
        'budget_position_id',
    )
    preventive_line_ids = fields.One2many(
        'public_budget.preventive_line',
        'budget_position_id',
    )
    assignment_position_id = fields.Many2one(
        'public_budget.budget_position',
        compute='_compute_assignment_position',
        store=True,
    )
    company_id = fields.Many2one(
        'res.company',
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
        help='Default Account on preventive lines of this position'
    )

    # @api.depends(
    #     'preventive_line_ids.affects_budget',
    #     'preventive_line_ids.transaction_id.state',
    #     'preventive_line_ids.preventive_amount',
    #     'preventive_line_ids.definitive_line_ids.amount',
    #     )
    def _compute_amounts(self):
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
        budget_id = self._context.get('budget_id', False)
        to_date = self._context.get('analysis_to_date', False)

        # we check it is a report because if not it will get wrong budget
        # on positions
        if not budget_id and 'aeroo_docs' in self._context:
            budget_id = self._context.get('budget_id', False)

        excluded_line_id = self._context.get('excluded_line_id', False)

        # if to_date use it, if not, then use now
        if to_date:
            day_of_year = fields.Datetime.from_string(
                to_date).timetuple().tm_yday
        else:
            day_of_year = datetime.now().timetuple().tm_yday

        _logger.info('Getting amounts for budget positions %s' % self.ids)
        for rec in self:
            if rec.type == 'view':
                operator = 'child_of'
            if rec.type == 'normal':
                operator = '='

            domain = [
                ('budget_position_id', operator, rec.id),
                # esto podria no ir porque el affects_budget ya tiene en cuetna
                # el estado de la transaccion
                ('transaction_id.state', 'in', ('open', 'closed')),
                ('affects_budget', '=', True),
            ]

            if budget_id:
                domain.append(('budget_id', '=', budget_id))
            if to_date:
                _logger.debug('Getting budget amounts with to_date %s' % (to_date))
                domain += [('transaction_id.issue_date', '<=', to_date)]

            # we add budget_assignment_allowed condition to optimize
            # if budget_id and self.budget_assignment_allowed:
            if budget_id and (rec.budget_assignment_allowed or rec.child_ids):
                modification_domain = [
                    ('budget_modification_id.budget_id', '=', budget_id),
                    ('budget_position_id', operator, rec.id)]
                if to_date:
                    modification_domain += [
                        ('budget_modification_id.date', '<=', to_date)]
                modification_lines = self.env[
                    'public_budget.budget_modification_detail'].search(
                        modification_domain)
                modification_amounts = [
                    line.amount for line in modification_lines]
                initial_lines = self.env[
                    'public_budget.budget_detail'].search([
                        ('budget_id', '=', budget_id),
                        ('budget_position_id', operator, rec.id)])
                initial_amounts = [
                    line.initial_amount for line in initial_lines]
                amount = sum(initial_amounts) + sum(modification_amounts)
            else:
                amount = False

            # we exclude lines from preventive lines because constraints
            # sometimes consider the line you are checking and sometimes
            #  not, so better we exclude that line and compare
            # to that line amount
            if excluded_line_id:
                domain.append(('id', '!=', excluded_line_id))

            rec.draft_amount = sum([x['preventive_amount'] for x in self.env[
                'public_budget.preventive_line'].read_group(
                domain=domain,
                fields=['budget_position_id', 'preventive_amount'],
                groupby=['budget_position_id'],
            )])

            # self.
            active_preventive_lines = self.env['public_budget.preventive_line'].with_context(
                prefetch_fields=False).search(domain)

            # TODO check if better performance by iterating once
            preventive_amount = sum(active_preventive_lines.mapped('preventive_amount'))
            rec.preventive_amount = preventive_amount
            rec.definitive_amount = sum(active_preventive_lines.mapped('definitive_amount_dynamic'))
            rec.to_pay_amount = sum(active_preventive_lines.mapped('to_pay_amount_dynamic'))
            rec.paid_amount = sum(active_preventive_lines.mapped('paid_amount_dynamic'))

            projected_amount = preventive_amount / day_of_year * 365
            rec.projected_amount = projected_amount

            if amount:
                rec.projected_avg = projected_amount / amount * 100.0
                rec.preventive_avg = preventive_amount / amount * 100.0
            rec.amount = amount
            rec.balance_amount = rec.amount - preventive_amount
            _logger.debug('Finish getting amounts for budget position %s' % rec.name)

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

    @api.constrains('child_ids', 'type', 'parent_id')
    def _check_type(self):
        for rec in self:
            if rec.child_ids and rec.type not in ('view'):
                raise ValidationError(_(
                    'You cannot define children to an account with '
                    'internal type different of "View".'))

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

    def get_parent_assignment_position(self):
        self.ensure_one()
        assignment_allowed = self.env['public_budget.budget_position']
        parent = self.parent_id
        while parent:
            if parent.budget_assignment_allowed:
                assignment_allowed += parent
            parent = parent.parent_id
        return assignment_allowed

    @api.depends(
        'parent_id',
        'child_ids',
        'budget_assignment_allowed',
    )
    def _compute_assignment_position(self):
        for rec in self:
            if rec.budget_assignment_allowed:
                assignment_position = rec
            else:
                assignment_position = rec.get_parent_assignment_position()
            rec.assignment_position_id = assignment_position.id

    def action_position_analysis_tree(self):
        self.ensure_one()
        res = {}
        display_name = '%s %s' % (self.code, self.name)
        if self.child_ids:
            action = self.env.ref(
                'public_budget.action_position_analysis_tree')
            res = action.read()[0]
            res['domain'] = [('id', 'in', self.child_ids.ids)]
            res['target'] = 'current'
            res['display_name'] = display_name
        elif self.preventive_line_ids:
            action = self.env.ref('public_budget.action_budget_position_items')
            res = action.read()[0]
            res['display_name'] = display_name
            res['context'] = {
                'search_default_budget_position_id': [self.id],
                'search_default_affects_budget': 1,
                'search_default_budget_id': self._context.get(
                    'budget_id', False)}
            if self._context.get('analysis_to_date', False):
                res['domain'] = [('transaction_id.issue_date', '<=', self._context.get('analysis_to_date', False))]
            res['target'] = 'current'
        return res

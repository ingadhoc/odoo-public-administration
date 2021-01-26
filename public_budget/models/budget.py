from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import time
import datetime


class Budget(models.Model):

    _name = 'public_budget.budget'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
    fiscalyear = fields.Char(
        required=True,
        default=time.strftime('%Y'),
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # TODO rename a default_income_account_id?
    # la dejamos por compatibilidad con CMR
    income_account_id = fields.Many2one(
        'account.account',
        string='Default Income Account',
        readonly=True,
        # required=True,
        states={'draft': [('readonly', False)]},
        domain="[('internal_type', '=', 'other'), "
        "('company_id', '=', company_id), "
        "('deprecated', '=', False)]",

    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
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
        compute='_compute_budget_positions'
    )
    budget_position_ids = fields.Many2many(
        relation='public_budget_budget_position_rel',
        comodel_name='public_budget.budget_position',
        # store=True, #TODO ver si agregamos el store
        compute='_compute_budget_positions'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company.id
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
    )
    state = fields.Selection(
        _states_,
        default='draft',
    )
    budget_modification_ids = fields.One2many(
        'public_budget.budget_modification',
        'budget_id',
        readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
        domain=[('initial_approval', '=', False)]
    )
    budget_detail_ids = fields.One2many(
        'public_budget.budget_detail',
        'budget_id',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    budget_prec_detail_ids = fields.One2many(
        'public_budget.budget_prec_detail',
        'budget_id',
        readonly=True
    )
    funding_move_ids = fields.One2many(
        'public_budget.funding_move',
        'budget_id',
        readonly=True,
        states={
            'open': [('readonly', False)],
            'pre_closed': [('readonly', False)]},
        context={'from_budget': True}
    )
    transaction_ids = fields.One2many(
        'public_budget.transaction',
        'budget_id',
    )
    receiptbook_id = fields.Many2one(
        'account.payment.receiptbook',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('partner_type', '=', 'supplier'), "
        "('company_id', '=', company_id)]",
    )

    @api.onchange('fiscalyear')
    @api.constrains('fiscalyear')
    def validate_fiscalyear(self):
        for rec in self:
            year = rec.fiscalyear
            if year.isdigit() and int(year) >= 1900 and int(year) <= 2099:
                continue
            raise ValidationError('%s no es un año valido!' % year)

    def check_date_in_budget_dates(self, date):
        """
        Verifica si una fecha esta dentro de las fechas del presupuesto
        """
        self.ensure_one()
        budget_dates = self.get_budget_fiscalyear_dates()
        date_from = budget_dates.get('date_from')
        date_to = budget_dates.get('date_to')
        if date_from <= date <= date_to:
            return True
        return False

    def get_budget_fiscalyear_dates(self):
        """
        Devolvemos para este budget primer y ultimo día del presupuesto
        segun configuración de la cia
        """
        self.ensure_one()
        last_month = self.company_id.fiscalyear_last_month
        last_day = self.company_id.fiscalyear_last_day
        date_to = datetime.date(int(self.fiscalyear), last_month, last_day)
        date_from = date_to + datetime.timedelta(days=1)
        date_from = date_from.replace(year=date_from.year - 1)
        return {'date_from': date_from, 'date_to': date_to}

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
        position_ids += budget_positions.search([('id', 'parent_of', position_ids)]).ids
        self.budget_position_ids = budget_positions.browse(
            list(set(position_ids))).sorted(key=lambda r: r.code)
        self.parent_budget_position_ids = self.budget_position_ids.filtered(
            lambda x: not x.parent_id)

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
        definitive_lines = self.env['public_budget.definitive_line'].search([
            ('budget_id', '=', self.id),
            ('transaction_id.state', 'in', ('open', 'closed'))])
        # definitive_lines = self.env['public_budget.definitive_line'].search(
        #     [('budget_id', '=', self.id)])
        # another way to do de same by SQL query
        # 'SELECT residual_amount '
        # 'FROM public_budget_definitive_line dl '
        # 'JOIN public_budget_transaction t '
        # 'ON dl.transaction_id = t.id '
        # 'WHERE dl.id IN %s AND t.state in [%s,%s]',
        # (tuple(definitive_lines.ids), 'open', 'closed'))
        passive_residue = 0.0
        if definitive_lines:
            self._cr.execute(
                'SELECT residual_amount '
                'FROM public_budget_definitive_line '
                'WHERE id IN %s', (tuple(definitive_lines.ids),))
            passive_residue = sum([x[0] for x in self._cr.fetchall()])
        self.passive_residue = passive_residue

    def action_cancel_draft(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'draft'})
        return True

    def action_open(self):
        self.write({'state': 'open'})
        return True

    def action_close(self):
        self.write({'state': 'closed'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

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
                    # 'parent_left': line.parent_left,
                    # 'order_int': line.parent_path,
                    'budget_id': rec.id,
                }
                rec.budget_prec_detail_ids.create(vals)
        self.write({'state': 'pre_closed'})

    def action_to_open_modification(self):
        self.ensure_one()
        view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'public_budget.view_budget_modification_detail_tree_inherit')
        view_search_id = self.env['ir.model.data'].xmlid_to_res_id(
            'public_budget.view_public_budget_modification_detail_filter')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Budget Modification Detail'),
            'res_model': 'public_budget.budget_modification_detail',
            'view_mode': 'tree',
            'view_id': view_id,
            'search_view_id': view_search_id,
            'target': 'current',
            'context': {'search_default_budget_id': self.id},

        }

    def action_to_open_definitive_lines(self):
        self.ensure_one()
        view_id = self.env.ref(
            'public_budget.view_public_budget_definitive_line_tree2').id
        view_search_id = self.env.ref(
            'public_budget.view_public_budget_definitive_line_filter').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Definitive Lines'),
            'res_model': 'public_budget.definitive_line',
            'view_mode': 'tree',
            'view_id': view_id,
            'search_view_id': view_search_id,
            'target': 'current',
            'domain': [('transaction_id.state', 'in', ['open', 'closed'])],
            'context': {'search_default_budget_id': self.id},

        }

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PublicBudgetExpedient(models.Model):

    _name = 'public_budget.expedient'
    _inherit = ['mail.thread']
    _description = 'Expedient'

    _order = "id desc"

    _states_ = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('annulled', 'Annulled'),
        ('cancel', 'Cancel'),
    ]

    number = fields.Char(
        readonly=True
    )
    issue_date = fields.Datetime(
        readonly=True,
        required=True,
        default=fields.Datetime.now
    )
    cover = fields.Char(
        compute='_compute_cover'
        # store=True,
    )
    description = fields.Char(
        required=True,
        # readonly=True,
        # states={'cancel': [('readonly', False)]}
    )
    reference = fields.Char(
        required=False
    )
    last_move_date = fields.Date(
        string='Last Move',
        store=True,
        compute_sudo=True,
        compute='_compute_current_location'
    )
    founder_id = fields.Many2one(
        'public_budget.expedient_founder',
        required=True
    )
    category_id = fields.Many2one(
        'public_budget.expedient_category',
        required=True
    )
    type = fields.Selection(
        [('payment', 'Payment'), ('authorizing', 'Authorizing')],
    )
    first_location_id = fields.Many2one(
        'public_budget.location',
        string='First Location',
        required=True
    )
    current_location_id = fields.Many2one(
        'public_budget.location',
        store=True,
        compute_sudo=True,
        compute='_compute_current_location'
    )
    last_location_id = fields.Many2one(
        'public_budget.location',
        store=True,
        compute_sudo=True,
        compute='_compute_current_location'
    )
    note = fields.Text(
    )
    pages = fields.Integer(
        required=True,
        track_visibility='onchange',
    )
    subsidy_expedient = fields.Boolean(
        string='Expediente de Solicitud Subsidio?',
        required=False
    )
    subsidy_recipient_doc = fields.Integer(
        string='DNI Receptor Potencial Subsidio',
        required=False
    )
    subsidy_amount = fields.Integer(
        string='Monto',
        required=False
    )
    subsidy_approved = fields.Boolean(
        string='Aprobado?',
        required=False
    )
    employee_subsidy_requestor = fields.Many2one(
        'res.partner',
        string='Empleado Solicitud',
        domain=[('employee', '=', True)]
    )
    final_location = fields.Char(
    )
    year = fields.Integer(
        compute='_compute_year'
    )
    in_transit = fields.Boolean(
        string='In Transit?',
        store=True,
        compute='_compute_current_location',
        compute_sudo=True,
    )
    user_location_ids = fields.Many2many(
        related='user_id.location_ids',
        readonly=True,
    )
    user_id = fields.Many2one(
        'res.users',
        readonly=True,
        required=True,
        default=lambda self: self.env.user
    )
    state = fields.Selection(
        _states_,
        default='open',
        track_visibility='onchange',
    )
    child_ids = fields.One2many(
        'public_budget.expedient',
        'parent_id',
        string='Childs'
    )
    parent_id = fields.Many2one(
        'public_budget.expedient',
        string='Parent'
    )
    supplier_ids = fields.Many2many(
        'res.partner',
        'public_budget_expedient_ids_supplier_ids_rel',
        'expedient_id',
        'partner_id',
        context={'default_supplier': 1},
        domain=[('supplier', '=', True)]
    )
    remit_ids = fields.Many2many(
        'public_budget.remit',
        'public_budget_remit_ids_expedient_ids_rel',
        'expedient_id',
        'remit_id',
        readonly=True,
        states={'in_transit': [('readonly', False)]}
    )
    parliamentary_expedient = fields.Char(
        string='Expediente Parlamentario'
    )
    overdue = fields.Boolean(
        string='Overdue?',
    )

    @api.depends(
        'first_location_id',
        'remit_ids',
        'remit_ids.location_id',
        'remit_ids.location_dest_id',
        'remit_ids.state',
    )
    def _compute_current_location(self):
        """
        current_location_id no es computed
        los otros dos si
        """
        for rec in self:
            last_move_date = False
            current_location_id = False
            last_location_id = False
            in_transit = False

            if rec.remit_ids:
                remits = rec.env['public_budget.remit'].search([
                    ('expedient_ids', '=', rec.id), ('state', '!=', 'cancel')],
                    order='date desc')
                if remits:
                    last_location_id = remits[0].location_id.id
                    current_location_id = remits[0].location_dest_id.id
                    last_move_date = remits[0].date
                    if remits[0].state == 'in_transit':
                        in_transit = True
                    else:
                        in_transit = False
            else:
                current_location_id = rec.first_location_id.id

            rec.last_location_id = last_location_id
            rec.current_location_id = current_location_id
            rec.last_move_date = last_move_date
            rec.in_transit = in_transit

    @api.constrains('pages')
    def check_pages_not_dni(self):
        for rec in self:
            if rec.pages > 10000:
                raise ValidationError(_(
                    'No puede poner número de páginas mayor a 10.000'))

    @api.onchange('subsidy_recipient_doc')
    def check_subsidy_recipient_doc(self):
        expedients_with_dni = self.search(
            [('subsidy_recipient_doc', '!=', 0),
                ('subsidy_recipient_doc', '=', self.subsidy_recipient_doc)])
        if len(expedients_with_dni) > 0:
            raise UserError(_(
                'El DNI ya existe en estos TA: \n * %s ' % ' \n * '.join(
                    expedients_with_dni.mapped('number'))))

    @api.multi
    def write(self, vals):
        if 'pages' in vals:
            new_pages = vals.get('pages')
            for record in self:
                if new_pages < record.pages:
                    raise ValidationError(_('No puede disminuir la cantidad '
                                            'de páginas de un '
                                            'expediente'))
        return super(PublicBudgetExpedient, self).write(vals)

    @api.multi
    def check_expedients_exist(self):
        for expedient in self:
            # no se puede si esta en transacciones no canceladas
            transactions = self.env['public_budget.transaction'].search([
                ('expedient_id', '=', expedient.id),
                ('state', '!=', 'cancel'),
            ])
            if transactions:
                raise ValidationError(_(
                    'No puede anular este expediente ya que es utilizado en '
                    'las siguientes transacciones %s' % transactions.ids))
            # no se puede si esta en payment_groups no cancelados
            payment_groups = self.env['account.payment.group'].search([
                ('expedient_id', '=', expedient.id),
                ('state', '!=', 'cancel'),
            ])
            if payment_groups:
                raise ValidationError(_(
                    'No puede anular este expediente ya que es utilizado en '
                    'las siguientes ordenes de pago %s' % payment_groups.ids))
        return True

    @api.depends('issue_date')
    def _compute_year(self):
        for rec in self:
            year = False
            if rec.issue_date:
                issue_date = fields.Datetime.from_string(rec.issue_date)
                year = issue_date.year
            rec.year = year

    @api.depends('supplier_ids', 'description')
    def _compute_cover(self):
        for rec in self:
            supplier_names = [x.name for x in rec.supplier_ids]
            cover = rec.description
            if supplier_names:
                cover += ' - ' + ', '.join(supplier_names)
            rec.cover = cover

    @api.multi
    def action_cancel_open(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'open'})
        return True

    @api.multi
    def action_close(self):
        self.write({'state': 'closed'})
        return True

    @api.multi
    def action_annulled(self):
        self.check_expedients_exist()
        self.write({'state': 'annulled'})
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id, "%s - %s" % (rec.number, rec.cover)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(
                [('number', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('cover', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.model
    def create(self, vals):
        vals['number'] = self.env[
            'ir.sequence'].with_context(
                ir_sequence_date=vals.get('issue_date')).next_by_code(
                'public_budget.expedient') or '/'
        return super(PublicBudgetExpedient, self).create(vals)

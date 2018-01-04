# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError


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
        store=True,
        compute='_get_cover'
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
        compute='_get_current_location'
    )
    founder_id = fields.Many2one(
        'public_budget.expedient_founder',
        string='Founder',
        required=True
    )
    category_id = fields.Many2one(
        'public_budget.expedient_category',
        string='Category',
        required=True
    )
    type = fields.Selection(
        [(u'payment', u'Payment'), (u'authorizing', u'Authorizing')],
    )
    first_location_id = fields.Many2one(
        'public_budget.location',
        string='First Location',
        required=True
    )
    current_location_id = fields.Many2one(
        'public_budget.location',
        string='Current Location',
        store=True,
        compute_sudo=True,
        compute='_get_current_location'
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
        compute='_get_year'
    )
    in_transit = fields.Boolean(
        string='In Transit?',
        store=True,
        compute='_get_current_location',
        compute_sudo=True,
    )
    user_location_ids = fields.Many2many(
        related='user_id.location_ids',
        readonly=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
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
        string='Suppliers',
        context={'default_supplier': 1},
        domain=[('supplier', '=', True)]
    )
    remit_ids = fields.Many2many(
        'public_budget.remit',
        'public_budget_remit_ids_expedient_ids_rel',
        'expedient_id',
        'remit_id',
        string='Remits',
        readonly=True,
        states={'in_transit': [('readonly', False)]}
    )
    parliamentary_expedient = fields.Char(
        string='Expediente Parlamentario'
    )

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        """
        Idea obtenida de aca
        https://github.com/odoo/odoo/issues/16072#issuecomment-289833419
        por el cambio que se introdujo en esa mimsa conversación, TODO en v11
        no haría mas falta, simplemente domain="[('id', 'in', x2m_field)]"
        Otras posibilidades que probamos pero no resultaron del todo fue:
        * agregar onchange sobre campos calculados y que devuelvan un dict con
        domain. El tema es que si se entra a un registro guardado el onchange
        no se ejecuta
        * usae el modulo de web_domain_field que esta en un pr a la oca
        """
        for field in field_onchange.keys():
            if field.startswith('user_location_ids.'):
                del field_onchange[field]
        return super(PublicBudgetExpedient, self).onchange(
            values, field_name, field_onchange)

    @api.multi
    @api.depends(
        'first_location_id',
        'remit_ids',
        'remit_ids.location_id',
        'remit_ids.location_dest_id',
        'remit_ids.state',
    )
    def _get_current_location(self):
        """
        current_location_id no es computed
        los otros dos si
        """
        for rec in self:
            last_move_date = False
            current_location_id = False
            in_transit = False

            if rec.remit_ids:
                remits = rec.env['public_budget.remit'].search([
                    ('expedient_ids', '=', rec.id), ('state', '!=', 'cancel')],
                    order='date desc')
                if remits:
                    current_location_id = remits[0].location_dest_id.id
                    last_move_date = remits[0].date
                    if remits[0].state == 'in_transit':
                        in_transit = True
                    else:
                        in_transit = False
            else:
                current_location_id = rec.first_location_id.id

            rec.current_location_id = current_location_id
            rec.last_move_date = last_move_date
            rec.in_transit = in_transit

    @api.multi
    @api.constrains('pages')
    def check_pages_not_dni(self):
        for rec in self:
            if rec.pages > 10000:
                raise ValidationError(
                    'No puede poner número de páginas mayor a 10.000')

    @api.multi
    def write(self, vals):
        if 'pages' in vals:
            new_pages = vals.get('pages')
            for record in self:
                if new_pages < record.pages:
                    raise ValidationError(
                        'No puede disminuir la cantidad de páginas de un '
                        'expediente')
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
                raise ValidationError(
                    'No puede anular este expediente ya que es utilizado en '
                    'las siguientes transacciones %s' % transactions.ids)
            # no se puede si esta en payment_groups no cancelados
            payment_groups = self.env['account.payment.group'].search([
                ('expedient_id', '=', expedient.id),
                ('state', '!=', 'cancel'),
            ])
            if payment_groups:
                raise ValidationError(
                    'No puede anular este expediente ya que es utilizado en '
                    'las siguientes ordenes de pago %s' % payment_groups.ids)
        return True

    @api.multi
    @api.depends('issue_date')
    def _get_year(self):
        for rec in self:
            year = False
            if rec.issue_date:
                issue_date = fields.Datetime.from_string(rec.issue_date)
                year = issue_date.year
            rec.year = year

    @api.multi
    @api.depends('supplier_ids', 'description')
    def _get_cover(self):
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

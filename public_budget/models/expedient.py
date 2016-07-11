# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class PublicBudgetExpedient(models.Model):
    """Expedient"""

    _name = 'public_budget.expedient'
    _description = 'Expedient'

    _order = "id desc"

    _states_ = [
        # State machine: untitle
        ('open', 'Open'),
        ('in_revision', 'In Revision'),
        ('closed', 'Closed'),
        ('annulled', 'Annulled'),
        ('cancel', 'Cancel'),
    ]

    number = fields.Char(
        string='Number',
        readonly=True
    )
    issue_date = fields.Datetime(
        string='Issue Date',
        readonly=True,
        required=True,
        default=fields.Datetime.now
    )
    cover = fields.Char(
        string=_('Cover'),
        store=True,
        compute='_get_cover'
    )
    description = fields.Char(
        string='Description',
        required=True,
        # readonly=True,
        # states={'cancel': [('readonly', False)]}
    )
    reference = fields.Char(
        string='Referencia',
        required=False
    )
    last_move_date = fields.Date(
        string=_('Last Move'),
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
        string='Type'
    )
    first_location_id = fields.Many2one(
        'public_budget.location',
        string='First Location',
        required=True
    )
    current_location_id = fields.Many2one(
        'public_budget.location',
        string=_('Current Location'),
        store=True,
        compute_sudo=True,
        compute='_get_current_location'
    )
    note = fields.Text(
        string='Note'
    )
    pages = fields.Integer(
        string='Pages',
        required=True
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
        string='Final Location'
    )
    year = fields.Integer(
        string=_('Año'),
        compute='_get_year'
    )
    in_transit = fields.Boolean(
        string=_('In Transit?'),
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
        'State',
        default='open',
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

    @api.one
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
        # self = self.sudo()
        last_move_date = False
        current_location_id = False
        in_transit = False

        if self.remit_ids:
            remits = self.env['public_budget.remit'].search([
                ('expedient_ids', '=', self.id), ('state', '!=', 'cancel')],
                order='date desc')
            if remits:
                current_location_id = remits[0].location_dest_id.id
                last_move_date = remits[0].date
                if remits[0].state == 'in_transit':
                    in_transit = True
                else:
                    in_transit = False
        else:
            current_location_id = self.first_location_id.id

        self.current_location_id = current_location_id
        self.last_move_date = last_move_date
        self.in_transit = in_transit

    @api.multi
    def write(self, vals):
        if 'pages' in vals:
            new_pages = vals.get('pages')
            for record in self:
                if new_pages < record.pages:
                    raise Warning(
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
                raise Warning(
                    'No puede anular este expediente ya que es utilizado en '
                    'las siguientes transacciones %s' % transactions.ids)
            # no se puede si esta en vouchers no cancelados
            vouchers = self.env['account.voucher'].search([
                ('expedient_id', '=', expedient.id),
                ('state', '!=', 'cancel'),
            ])
            if vouchers:
                raise Warning(
                    'No puede anular este expediente ya que es utilizado en '
                    'las siguientes ordenes de pago %s' % vouchers.ids)
        return True

    @api.one
    @api.depends('issue_date')
    def _get_year(self):
        """"""
        year = False
        if self.issue_date:
            issue_date = fields.Datetime.from_string(self.issue_date)
            year = issue_date.year
        self.year = year

    @api.one
    @api.depends('supplier_ids', 'description')
    def _get_cover(self):
        """"""
        supplier_names = [x.name for x in self.supplier_ids]
        cover = self.description
        if supplier_names:
            cover += ' - ' + ', '.join(supplier_names)
        self.cover = cover

    @api.multi
    def action_cancel_open(self):
        """ go from canceled state to draft state"""
        self.write({'state': 'open'})
        self.delete_workflow()
        self.create_workflow()
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
            'ir.sequence'].get('public_budget.expedient') or '/'
        return super(PublicBudgetExpedient, self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

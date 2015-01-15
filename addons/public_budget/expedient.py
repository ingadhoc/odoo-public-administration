# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class expedient(models.Model):
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

    issue_date = fields.Datetime(
        string='Issue Date',
        required=True,
        default=fields.Datetime.now
        )
    number = fields.Char(
        string='Number',
        required=True,
        default=lambda self: self.env['ir.sequence'].get('public_budget.expedient')
        )
    cover = fields.Char(
        string='Cover',
        store=True,
        compute='_get_cover'
        )
    description = fields.Char(
        string='Description',
        required=True
        )
    last_move_date = fields.Date(
        string='Last Move',
        store=True,
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
    first_location_id = fields.Many2one(
        'public_budget.location',
        string='First Location'
        )
    type = fields.Selection(
        [(u'payment', u'Payment'), (u'authorizing', u'Authorizing')],
        string='Type'
        )
    current_location_id = fields.Many2one(
        'public_budget.location',
        string='Current Location',
        store=True,
        compute='_get_current_location'
        )
    note = fields.Html(
        string='Note'
        )
    final_location = fields.Char(
        string='Final Location'
        )
    year = fields.Integer(
        string='Year',
        compute='_get_year'
        )
    state = fields.Selection(
        _states_,
        'State',
        default='open',
        )
    expedient_move_ids = fields.One2many(
        'public_budget.expedient_move',
        'expedient_id',
        string='Moves'
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

    _constraints = [
    ]

    @api.one
    @api.depends(
        'first_location_id',
        'expedient_move_ids',
        'expedient_move_ids.location_dest_id',
        'expedient_move_ids.date')
    def _get_current_location(self):
        """"""
        moves = self.env['public_budget.expedient_move'].search([
            ('expedient_id', '=', self.id)], order='date desc')
        last_move_date = False
        if moves:
            self.current_location_id = moves[0].location_dest_id.id
            last_move_date = moves[0].date
        elif self.first_location_id:
            self.current_location_id = self.first_location_id.id
        else:
            self.current_location_id = False
        self.last_move_date = last_move_date

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
        # go from canceled state to draft state
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

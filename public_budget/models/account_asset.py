from odoo import api, fields, models, _


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    _order = 'reference'

    active = fields.Boolean(
        tracking=True,
        default=True,
    )
    enrollment = fields.Char()
    reference = fields.Char()
    serial_number = fields.Char()
    asset_state = fields.Selection(
        [('n', 'N'),
            ('b', 'B'),
            ('r', 'R'),
            ('m', 'M')],
        default='n',
    )
    observations = fields.Text()
    location_id = fields.Many2one(
        'public_budget.location',
        tracking=True,
        domain="[('asset_management', '=', True)]",
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
    )
    user_id = fields.Many2one(
        'res.users',
        related='location_id.user_id',
    )
    visible_button_transfer_asset = fields.Boolean(
        compute='_compute_visible_button_transfer_asset')

    transit = fields.Boolean(
        readonly=True,
    )
    comodato = fields.Boolean(
        'Comodato?'
    )
    patrimonial = fields.Boolean(
        'Patrimonial?'
    )
    reportable = fields.Boolean(
        'Reportable?'
    )
    transaction_ids = fields.One2many(
        'public_budget.transaction',
        compute='_compute_transaction_ids',
        compute_sudo=True,
    )
    level = fields.Char(
        related='location_id.level',
    )
    number = fields.Char(
        related='location_id.number',
    )
    building = fields.Char(
        related='location_id.building',
    )
    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
        states={'draft': [('readonly', False)]})

    _sql_constraints = [
        ('reference', 'unique(reference)',
         '¡La referencia debe ser unica!')]

    def _compute_transaction_ids(self):
        PublicBudgetTransaction = self.env['public_budget.transaction']
        assets = self.filtered('invoice_id')
        (self - assets).update({'transaction_ids': PublicBudgetTransaction})
        for rec in assets:
            domain = [('invoice_ids', 'in', [rec.invoice_id.id])]
            rec.transaction_ids = PublicBudgetTransaction.search(domain)

    def _compute_visible_button_transfer_asset(self):
        assets = self.filtered(lambda x: x.user_id == self.env.user)
        (self - assets).update({'visible_button_transfer_asset': False})
        for rec in assets:
            rec.visible_button_transfer_asset = True

    def transfer_asset(self):
        self.ensure_one()
        action = self.env.ref(
            'public_budget.action_transfer_asset_wizard')
        action_read = action.sudo().read()[0]
        return action_read

    def confirm_tranfer(self):
        self.ensure_one()
        self.transit = False
        body = _(
            'The User "%s" confirm transfer asset'
            ' to the location "%s"') % (
            self.env.user.name, self.location_id.name)
        self.message_post(body=body)
        return True

    # We overwrite this method to block the odoo funcionality to send a
    # message whit the fields that not interested to show
    def validate(self):
        self.write({'state': 'open'})

    def action_view_transaction(self):
        self.ensure_one()
        action = self.env.ref(
            'public_budget.action_public_budget_transaction_transactions')
        action = action.sudo().read()[0]
        action['domain'] = [('id', 'in', self.transaction_ids.ids)]
        return action

    @api.model
    def create(self, values):
        if not values.get('reference', False):
            values['reference'] = self.env['ir.sequence'].next_by_code(
                'public_budget.asset')
        return super().create(values)

    def archive_and_close_asset(self):
        self.write({'state': 'close', 'active': False})

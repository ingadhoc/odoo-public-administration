from odoo import api, fields, models, _


class AccountAssetAsset(models.Model):
    _name = 'account.asset.asset'
    _inherit = ['account.asset.asset', 'mail.activity.mixin']

    enrollment = fields.Char(
    )
    reference = fields.Char(
        default=lambda self: self._get_default_code(),
    )
    serial_number = fields.Char(
    )
    asset_state = fields.Selection(
        [('n', 'N'),
            ('b', 'B'),
            ('r', 'R'),
            ('m', 'M')],
        required=True,
        default='n',
    )
    observations = fields.Text(

    )
    location_id = fields.Many2one(
        'public_budget.location',
        track_visibility='onchange',
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
    )
    user_id = fields.Many2one(
        'res.users',
        related='location_id.user_id',
        readonly=True,
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
    )
    level = fields.Char()
    number = fields.Char()

    _sql_constraints = [
        ('reference', 'unique(reference)',
         '¡La referencia debe ser unica!')]

    @api.model
    def _get_default_code(self):
        return self.env['ir.sequence'].next_by_code('public_budget.asset')

    @api.multi
    def _compute_transaction_ids(self):
        for rec in self.filtered('invoice_id'):
            domain = [('invoice_ids', 'in', [rec.invoice_id.id])]
            rec.transaction_ids = self.env['public_budget.transaction'].search(
                domain)

    @api.multi
    def _compute_visible_button_transfer_asset(self):
        for rec in self.filtered(lambda x: x.user_id == self.env.user):
            rec.visible_button_transfer_asset = True

    @api.multi
    def transfer_asset(self):
        self.ensure_one()
        action = self.env.ref(
            'public_budget.action_transfer_asset_wizard')
        action_read = action.read()[0]
        return action_read

    @api.multi
    def confirm_tranfer(self):
        self.ensure_one()
        self.transit = False
        body = _(
            'The User "%s" confirm transfer asset'
            ' to the location "%s"') % (
            self.env.user.name, self.location_id.name)
        self.message_post(body)
        return True

    # We overwrite this method to block the odoo funcionality to send a
    # message whit the fields that not interested to show
    @api.multi
    def validate(self):
        self.write({'state': 'open'})

    @api.multi
    def action_view_transaction(self):
        self.ensure_one()
        action = self.env.ref(
            'public_budget.action_public_budget_transaction_transactions')
        action = action.read()[0]
        action['domain'] = [('id', 'in', self.transaction_ids.ids)]
        return action

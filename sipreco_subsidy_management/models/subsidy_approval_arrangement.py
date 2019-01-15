from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class ApprovalArrangement(models.Model):

    _name = 'public_budget.subsidy.approval_arrangement'
    _rec_name = 'number'

    number = fields.Char(
        required=True,
        readonly=True,
        # default=_get_number,
    )
    fojas = fields.Integer(
        required=True,
    )
    rendition_ids = fields.One2many(
        'public_budget.subsidy.rendition',
        'approval_arrangement_id',
        # required=True,
    )
    # rendition_id = fields.Many2one(
    #     'public_budget.subsidy.rendition',
    #     'Rendición',
    #     required=True,
    # )
    # subsidy_id = fields.Many2one(
    #     'public_budget.subsidy',
    #     'Subsidio',
    #     required=True,
    # )
    currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_currency'
    )
    approved_amount = fields.Monetary(
        'Monto Aprobado',
        required=True,
        # default=_get_approved_amount,
    )

    _sql_constraints = [
        ('number_unique', 'unique(number)',
            ('El número debe ser único en las disposiciones de aprobación'))]

    # @api.model
    # def _get_approved_amount(self):
    #     # lo hacemos asi porque mandando por vista nos daba error
    #     rendition_id = self._context.get('default_rendition_id')
    #     if rendition_id:
    #         return self.env['public_budget.subsidy.rendition'].browse(
    #             rendition_id).rendition_amount
    #     return False

    @api.model
    def create(self, vals):
        if not vals.get('number'):
            vals['number'] = self.env['ir.sequence'].next_by_code(
                'approval_arrangement')
        return super(ApprovalArrangement, self).create(vals)

    @api.multi
    def _compute_currency(self):
        currency = self.env.user.company_id.currency_id
        for rec in self:
            rec.currency_id = currency

    @api.multi
    def action_view_subsidy(self):
        subsidies = self.mapped('rendition_ids.subsidy_id')
        action = self.env.ref(
            'sipreco_subsidy_management.action_public_budget_subsidy')
        if not action:
            return True
        action_read = action.read()[0]
        action_read['domain'] = [('id', 'in', subsidies.ids)]
        return action_read

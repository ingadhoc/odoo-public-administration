from odoo import models, fields


class InventoryRule(models.Model):
    """"""

    _name = 'public_budget.inventory_rule'
    _description = 'Inventory Rule'

    date = fields.Date(
        required=True,
        default=fields.Date.context_today
    )
    min_amount = fields.Monetary(
        string='Minimum Amount',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'public_budget.inventory_rule')
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True,
    )

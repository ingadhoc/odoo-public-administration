from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    inventory_rule_ids = fields.One2many(
        'public_budget.inventory_rule',
        'company_id',
        string='Inventory Rules'
    )

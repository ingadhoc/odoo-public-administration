from odoo import models, fields


class PublicBudgetExpedient(models.Model):

    _inherit = 'public_budget.expedient'

    purchase_order_ids = fields.One2many(
        'purchase.order',
        'expedient_id',
    )

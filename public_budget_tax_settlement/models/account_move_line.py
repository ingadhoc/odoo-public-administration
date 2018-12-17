from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    payment_methods = fields.Char(
        'Payment Methods',
        related='payment_id.payment_group_id.payment_methods'
    )

##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class PurchaseWebAward(models.Model):
    _name = 'purchase.web.award'
    _description = 'Adjudicatario de Solicitud de Compra'
    _order = 'requisition_id, id'

    requisition_id = fields.Many2one(
        'purchase.requisition',
        string='Solicitud de Compra',
        required=True,
        ondelete='cascade',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Adjudicatario',
        required=True,
    )
    amount = fields.Monetary(
        string='Valor adjudicado',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        related='requisition_id.currency_id',
        store=True,
    )
    notes = fields.Char(
        string='Detalle',
    )

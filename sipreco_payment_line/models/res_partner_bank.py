from odoo import models, fields


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    numero_de_sucursal = fields.Char(
    )

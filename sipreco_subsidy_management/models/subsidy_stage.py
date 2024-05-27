from odoo import fields, models


class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'

    is_verified = fields.Boolean(string='Verificar Etapa')

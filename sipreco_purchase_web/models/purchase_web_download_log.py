##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class PurchaseWebDownloadLog(models.Model):
    _name = 'purchase.web.download.log'
    _description = 'Log de descargas de archivos públicos'
    _order = 'download_date desc'

    attachment_line_id = fields.Many2one(
        'purchase.web.attachment',
        string='Archivo',
        required=True,
        ondelete='cascade',
    )
    requisition_id = fields.Many2one(
        related='attachment_line_id.requisition_id',
        store=True,
        string='Solicitud de Compra',
    )
    email = fields.Char(
        string='Email',
        required=True,
    )
    download_date = fields.Datetime(
        string='Fecha de descarga',
        default=fields.Datetime.now,
        readonly=True,
    )

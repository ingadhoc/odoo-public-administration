##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields


class PurchaseWebAttachment(models.Model):
    _name = 'purchase.web.attachment'
    _description = 'Archivo público de Solicitud de Compra'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    requisition_id = fields.Many2one(
        'purchase.requisition',
        string='Solicitud de Compra',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(
        string='Descripción',
        required=True,
    )
    attachment_type = fields.Selection(
        selection=[
            ('pliego', 'Pliego'),
            ('circular', 'Circular aclaratoria/modificatoria'),
            ('ddjj', 'Declaración jurada'),
            ('other', 'Otro'),
        ],
        string='Tipo',
        default='other',
        required=True,
    )
    attachment = fields.Binary(
        string='Archivo',
    )
    attachment_fname = fields.Char(
        string='Nombre del archivo',
    )
    require_email = fields.Boolean(
        string='Solicitar email para descarga',
        default=False,
    )
    download_log_ids = fields.One2many(
        'purchase.web.download.log',
        'attachment_line_id',
        string='Log de descargas',
    )
    download_count = fields.Integer(
        string='Descargas',
        compute='_compute_download_count',
    )

    @api.depends('download_log_ids')
    def _compute_download_count(self):
        grouped = self.env['purchase.web.download.log'].read_group(
            [('attachment_line_id', 'in', self.ids)],
            ['attachment_line_id'],
            ['attachment_line_id'],
        )
        counts = {g['attachment_line_id'][0]: g['attachment_line_id_count'] for g in grouped}
        for rec in self:
            rec.download_count = counts.get(rec.id, 0)

    def action_view_download_logs(self):
        self.ensure_one()
        return {
            'name': 'Descargas — %s' % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.web.download.log',
            'view_mode': 'list',
            'domain': [('attachment_line_id', '=', self.id)],
            'context': {'create': False},
        }

##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    # -------------------------------------------------------------------------
    # Publicación web
    # -------------------------------------------------------------------------
    web_publishable = fields.Boolean(
        string='Publicable en web',
        default=False,
    )
    website_published = fields.Boolean(
        string='Publicado en web',
        default=False,
        copy=False,
    )

    # Datos públicos de identificación
    web_number = fields.Char(
        string='Número',
        copy=False,
    )
    web_object = fields.Char(
        string='Objeto',
    )
    web_amount = fields.Monetary(
        string='Valor oficial',
        currency_field='currency_id',
    )
    web_amount_manual = fields.Boolean(
        string='Monto manual',
        default=False,
        help='Si está activo, el valor oficial no se toma de la SC sino que se carga manualmente.',
    )

    # Fechas públicas
    web_opening_datetime = fields.Datetime(
        string='Fecha y hora de Apertura',
    )
    web_publication_date = fields.Date(
        string='Fecha de publicación',
        copy=False,
    )
    web_last_update = fields.Datetime(
        string='Fecha última actualización',
        copy=False,
    )

    # Estado público
    web_state = fields.Selection(
        selection=[
            ('open', 'Para Apertura'),
            ('evaluation', 'En evaluación'),
            ('awarded', 'Adjudicada'),
            ('finished', 'Finalizada'),
            ('void', 'Desierta'),
            ('failed', 'Fracasada'),
            ('suspended', 'Suspendida'),
        ],
        string='Estado público',
        default='open',
    )

    # Observaciones
    web_observations = fields.Html(
        string='Observaciones',
        sanitize=True,
    )

    # Relaciones con adjudicatarios (solo cuando web_state == 'finished')
    web_award_ids = fields.One2many(
        'purchase.web.award',
        'requisition_id',
        string='Adjudicatarios',
    )
    web_total_awarded = fields.Monetary(
        string='Valor total adjudicado',
        currency_field='currency_id',
        compute='_compute_web_total_awarded',
        store=True,
    )

    # Archivos públicos
    web_attachment_ids = fields.One2many(
        'purchase.web.attachment',
        'requisition_id',
        string='Archivos públicos',
    )

    # -------------------------------------------------------------------------
    # Computes
    # -------------------------------------------------------------------------
    @api.depends('web_award_ids.amount')
    def _compute_web_total_awarded(self):
        grouped = self.env['purchase.web.award'].read_group(
            [('requisition_id', 'in', self.ids)],
            ['requisition_id', 'amount:sum'],
            ['requisition_id'],
        )
        totals = {g['requisition_id'][0]: g['amount'] for g in grouped}
        for rec in self:
            rec.web_total_awarded = totals.get(rec.id, 0.0)

    @api.onchange('web_amount_manual', 'amount_total')
    def _onchange_web_amount_manual(self):
        if not self.web_amount_manual:
            self.web_amount = self.amount_total

    # -------------------------------------------------------------------------
    # Acciones
    # -------------------------------------------------------------------------
    def action_web_publish(self):
        for rec in self:
            if not rec.web_publishable:
                continue
            rec.website_published = True
            if not rec.web_publication_date:
                rec.web_publication_date = fields.Date.today()
            rec.web_last_update = fields.Datetime.now()

    def action_web_unpublish(self):
        for rec in self:
            rec.website_published = False

    def action_view_website(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/compras/%d' % self.id,
            'target': 'new',
        }

    @api.onchange('web_publishable')
    def _onchange_web_publishable(self):
        if not self.web_publishable and self.website_published:
            self.website_published = False

    def write(self, vals):
        if 'web_publishable' in vals and not vals['web_publishable']:
            vals['website_published'] = False
        web_fields = {
            'web_number', 'web_object', 'web_amount', 'web_amount_manual',
            'web_opening_datetime', 'web_state', 'web_observations',
            'web_attachment_ids', 'web_award_ids',
        }
        if vals.keys() & web_fields and self.filtered('website_published') and 'web_last_update' not in vals:
            vals['web_last_update'] = fields.Datetime.now()
        return super().write(vals)

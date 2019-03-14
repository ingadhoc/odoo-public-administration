##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    name = fields.Char(
        # cambiamos string
        'Reference',
    )
    manual_request_ids = fields.One2many(
        'stock.request',
        'manual_requisition_id',
        'Request',
        # 'stock.move',
        # 'requisition_id',
        # 'Supply Requirements',
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        'Tramite Administrativo',
        ondelete='restrict',
    )
    transaction_type_id = fields.Many2one(
        'public_budget.transaction_type',
        string='Type',
        # readonly=True,
        # states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id)]",
        track_visibility='onchange',
    )

    inspected = fields.Boolean(
        'Inspected?'
    )

    amount_total = fields.Float(
        digits=dp.get_precision('Product Price'),
        compute='_compute_amount_total',
    )

    date = fields.Date(
        'Start Date',
        readonly=True,
    )
    user_inspected_id = fields.Many2one(
        'res.users',
        track_visibility='onchange',
    )
    user_confirmed_id = fields.Many2one(
        'res.users',
        track_visibility='onchange',
    )

    printed = fields.Boolean(
        'printed?',
    )

    @api.depends('line_ids')
    def _compute_amount_total(self):
        for rec in self.filtered('line_ids'):
            rec.amount_total = sum([x.subtotal for x in rec.line_ids])

    @api.multi
    def to_inspected(self):
        if not self.transaction_type_id:
            raise UserError(_('Antes de revisar debe tener establecido un'
                              '"Tipo"'))
        self.inspected = True
        self.user_inspected_id = self.env.user

    @api.multi
    def action_draft(self):
        if self.state == 'draft' and self.inspected:
            self.inspected = False
        elif self.state == 'in_progress':
            self.with_context(cancel_procurement=False).action_cancel()
        super(PurchaseRequisition, self).action_draft()

    @api.multi
    def action_cancel(self):
        if self._context.get('cancel_procurement', True):
            self.mapped('manual_procurement_ids').button_cancel_remaining()
        self.inspected = False
        self.user_inspected_id = False
        self.user_confirmed_id = False
        return super(PurchaseRequisition, self).action_cancel()

    @api.multi
    def action_open(self):
        for rec in self:
            if not rec.purchase_ids:
                raise UserError(_(
                    'No se puede cerrar la licitación si no se solicitaron '
                    'presupuestos'))
        return super(PurchaseRequisition, self).action_open()

    @api.model
    def create(self, vals):
        vals['date'] = fields.Date.today()
        return super(PurchaseRequisition, self).create(vals)

    @api.multi
    def action_in_progress(self):
        self.user_confirmed_id = self.env.user
        super(PurchaseRequisition, self).action_in_progress()

    @api.multi
    def print_report_requisition(self):
        self.ensure_one()
        action = self.env.ref(
            'sipreco_purchase.action_aeroo_purchase_requisition_report')
        body = _("User: %s printed the report: %s" %
                 (self.env.user.name, action.name))
        self.message_post(body=body)
        if not self.printed:
            self.printed = True
        return action.read()[0]

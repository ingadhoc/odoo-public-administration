##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    state = fields.Selection(
        tracking=True,
    )

   # Cambiamos el default para que no requira tener vendor por defecto
    requisition_type = fields.Selection(default='purchase_template')
    manual_request_ids = fields.One2many(
        'stock.request',
        'manual_requisition_id',
        'Request',
    )
    expedient_id = fields.Many2one(
        'public_budget.expedient',
        'Tramite Administrativo',
        ondelete='restrict',
    )
    transaction_type_id = fields.Many2one(
        'public_budget.transaction_type',
        string='Type',
        domain="[('company_id', '=', company_id)]",
        tracking=True,
    )

    inspected = fields.Boolean(
        'Inspected?'
    )

    amount_total = fields.Float(
        digits='Product Price',
        compute='_compute_amount_total',
    )

    date = fields.Date(
        'Date',
        readonly=True,
    )
    user_inspected_id = fields.Many2one(
        'res.users',
        tracking=True,
    )
    user_confirmed_id = fields.Many2one(
        'res.users',
        tracking=True,
    )

    printed = fields.Boolean(
        'printed?',
    )

    route_id = fields.Many2one(
        'stock.route',
    )

    route_ids = fields.Many2many(
        'stock.route',
        compute='_compute_route_ids',
        readonly=True,
        string="Routes"
    )

    @api.depends('user_id')
    def _compute_route_ids(self):
        for rec in self:
            user_picking_type_ids = self.env.user.picking_type_ids.ids
            rec.route_ids = self.env['stock.route'].search(
                [('rule_ids.picking_type_id', 'in', user_picking_type_ids)])

    @api.depends('line_ids')
    def _compute_amount_total(self):
        self.update({'amount_total': 0.0})
        for rec in self.filtered('line_ids'):
            rec.amount_total = sum([x.subtotal for x in rec.line_ids])

    def to_inspected(self):
        for rec in self:
            if not rec.transaction_type_id:
                raise UserError(_('Antes de revisar debe tener establecido un'
                                '"Tipo"'))

            rec.inspected = True
            rec.user_inspected_id = self.env.user

    def revert_inspection(self):
        for rec in self.filtered('inspected'):
            rec.inspected = False
            rec.user_inspected_id = False


    def action_cancel(self):
        if self._context.get('cancel_procurement', True):
            self.mapped('manual_request_ids').button_cancel_remaining()
        self.inspected = False
        self.user_inspected_id = False
        self.user_confirmed_id = False
        return super().action_cancel()

    def action_open(self):
        for rec in self:
            if not rec.purchase_ids:
                raise UserError(_(
                    'No se puede cerrar la licitación si no se solicitaron '
                    'presupuestos'))
        return super().action_open()

    @api.model
    def create(self, vals):
        vals['date'] = fields.Date.today()
        vals['name'] = self.env['ir.sequence'].next_by_code(
                'purchase.requisition.purchase.tender') or 'New'
        return super().create(vals)

    def action_confirm(self):
        if self.amount_total <= 0:
            raise UserError(_('No se puede confirmar una requisición sin '
                              'líneas o con importe total 0.'))
        self.user_confirmed_id = self.env.uid
        super().action_confirm()

    def print_report_requisition(self):
        self.ensure_one()
        action = self.env.ref('sipreco_purchase.action_aeroo_purchase_requisition_report').report_action(self, config=False)
        body = _("User: %s printed the report: %s" %
                 (self.env.user.name, action.get('name')))
        self.message_post(body=body)
        if not self.printed:
            self.printed = True
        return action

    def action_send_imputation_notice(self):
        self.ensure_one()
        template = self.env.ref(
            'sipreco_purchase.mail_template_purchase_requisition_imputada',
            raise_if_not_found=False,
        )
        ctx = {
            'default_model': 'purchase.requisition',
            'default_res_ids': self.ids,
            'default_use_template': bool(template),
            'default_template_id': template.id if template else False,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_draft(self):
        """ We need to keep the original number for the order regardless of change the state
        """
        self.ensure_one()
        name = self.name
        super().action_draft()
        self.name = name

    @api.depends('vendor_id','user_id')
    def _compute_currency_id(self):
        for requisition in self:
            if not requisition.vendor_id or not requisition.vendor_id.property_purchase_currency_id:
                requisition.currency_id = requisition.company_id.currency_id.id
            else:
                requisition.currency_id = requisition.vendor_id.property_purchase_currency_id.id

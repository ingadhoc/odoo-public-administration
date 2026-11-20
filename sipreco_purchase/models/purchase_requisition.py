##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


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

    @api.model_create_multi
    def create(self, vals_list):
        # el name lo asigna el core; ver ir.sequence.next_by_code
        for vals in vals_list:
            vals['date'] = fields.Date.today()
        return super().create(vals_list)

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

    def _get_comparative_quotes(self, purchase):
        """Match the lines of ``purchase`` with the requisition lines.

        Returns ``{requisition line id: purchase.order.line}``: the quoted line
        first and then the alternatives the vendor added for that item. There
        is no field linking both lines, so they are matched in three steps:

        1. same product and description (the order line copied it from the
           requisition);
        2. same product, keeping the order of both documents: the lines are
           aligned (longest common subsequence of products), so an extra line
           of a product is skipped when pairing it would break the order of
           the next items. Vendors may quote fewer units, so the quantity only
           breaks ties between alignments with the same number of pairs;
        3. same product, whatever the order (the order lines were reordered).

        Each left over line goes to the item whose line is the closest above
        it, or to the first item of the product when there is none above.
        Unless the item was matched by description, the first line of its
        group is the quoted one and the next ones are alternatives.
        """
        self.ensure_one()
        order_lines = purchase.order_line.filtered(lambda line: not line.display_type)
        position = {line.id: index for index, line in enumerate(order_lines)}
        free = list(order_lines)
        quoted = {}

        for req_line in self.line_ids:
            description = (req_line.name or '').strip()
            order_line = description and next((
                o for o in free
                if o.product_id == req_line.product_id and (o.name or '').strip() == description), None)
            if order_line:
                quoted[req_line.id] = order_line
                free.remove(order_line)
        by_description = set(quoted)

        pending = [r for r in self.line_ids if r.id not in quoted]
        pair_weight = len(pending) + 1

        def weight(req_line, order_line):
            # a pair always beats any number of quantity ties
            if req_line.product_id != order_line.product_id:
                return 0
            return pair_weight + (not float_compare(
                order_line.product_qty, req_line.product_qty,
                precision_rounding=req_line.product_uom_id.rounding or 0.01))

        # score[i][j]: best alignment of pending[i:] with free[j:]
        score = [[0] * (len(free) + 1) for _ in range(len(pending) + 1)]
        for i in range(len(pending) - 1, -1, -1):
            for j in range(len(free) - 1, -1, -1):
                pair = weight(pending[i], free[j])
                score[i][j] = max(
                    score[i + 1][j], score[i][j + 1],
                    pair and pair + score[i + 1][j + 1])
        i = j = 0
        aligned = []
        while i < len(pending) and j < len(free):
            pair = weight(pending[i], free[j])
            if pair and score[i][j] == pair + score[i + 1][j + 1]:
                aligned.append((pending[i], free[j]))
                i += 1
                j += 1
            elif score[i + 1][j] >= score[i][j + 1]:
                i += 1
            else:
                j += 1
        for req_line, order_line in aligned:
            quoted[req_line.id] = order_line
            free.remove(order_line)

        for req_line in self.line_ids:
            if req_line.id in quoted:
                continue
            order_line = next((o for o in free if o.product_id == req_line.product_id), None)
            if order_line:
                quoted[req_line.id] = order_line
                free.remove(order_line)

        item_by_line = {o.id: r for r, o in quoted.items()}
        groups = {r: [o] for r, o in quoted.items()}
        for order_line in free:
            same_product = sorted(
                (o for o in quoted.values() if o.product_id == order_line.product_id),
                key=lambda o: position[o.id])
            if not same_product:
                continue
            above = [o for o in same_product if position[o.id] < position[order_line.id]]
            groups[item_by_line[(above[-1] if above else same_product[0]).id]].append(order_line)

        empty = purchase.order_line.browse()
        result = {}
        for req_line in self.line_ids:
            lines = groups.get(req_line.id, [])
            if req_line.id in by_description:
                lines = lines[:1] + sorted(lines[1:], key=lambda o: position[o.id])
            else:
                lines = sorted(lines, key=lambda o: position[o.id])
            result[req_line.id] = empty.concat(*lines)
        return result

    def get_comparative_rows(self):
        """Rows of the price comparison report.

        One row per requisition line, followed by one row per alternative
        («N (opción 2)», …) when some vendor quoted more than one line for the
        item. ``quotes`` maps each purchase id to the order line of that row,
        or to an empty recordset when the vendor has nothing for it.
        """
        self.ensure_one()
        purchases = self.purchase_ids.filtered(lambda p: p.state != 'cancel')
        quotes = {p.id: self._get_comparative_quotes(p) for p in purchases}
        empty = self.env['purchase.order.line']
        rows = []
        for number, req_line in enumerate(self.line_ids, start=1):
            options = max([len(quotes[p.id][req_line.id]) for p in purchases] + [1])
            for option in range(options):
                rows.append({
                    'number': number if not option else '%s (opción %s)' % (number, option + 1),
                    'line': req_line,
                    'quotes': {
                        p.id: quotes[p.id][req_line.id][option:option + 1] or empty
                        for p in purchases
                    },
                })
        return rows

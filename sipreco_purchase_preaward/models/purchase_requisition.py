##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, fields, models
from odoo.exceptions import UserError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    preaward_dismissal = fields.Text(
        'Desestimación',
        copy=False,
        help='Ofertas que se desestiman y su motivo. Sale en la planilla de preadjudicación.',
    )
    preaward_justification = fields.Text(
        'Justificación de la recomendación',
        copy=False,
        help='Fundamento de la preadjudicación. Sale en la planilla de preadjudicación.',
    )
    preaward_user_id = fields.Many2one(
        'res.users',
        'Preadjudicada por',
        readonly=True,
        copy=False,
    )
    preaward_date = fields.Datetime(
        'Fecha de preadjudicación',
        readonly=True,
        copy=False,
    )

    def print_preaward_report(self):
        """Preaward sheet. Stamps who printed it first and when."""
        self.ensure_one()
        action = self.env.ref(
            'sipreco_purchase_preaward.action_report_purchase_requisition_preaward').report_action(self, config=False)
        if not self.preaward_user_id:
            self.write({
                'preaward_user_id': self.env.uid,
                'preaward_date': fields.Datetime.now(),
            })
        return action

    def action_clear_unawarded_quantities(self):
        """Zeroes the quantity of the lines left out of the preaward.

        Quotations already confirmed or cancelled stay untouched:
        action_clear_quantities of purchase_requisition filters them out.
        """
        self.ensure_one()
        lines = self.purchase_ids.order_line.filtered(lambda x: not x.preaward and x.product_qty)
        if not lines:
            raise UserError(_('No hay líneas sin preadjudicar con cantidad para poner en cero.'))
        lines.action_clear_quantities()

    def action_open_quotation_lines(self):
        """Lines of every quotation of the requisition, to tick the preawarded ones."""
        self.ensure_one()
        return {
            'name': _('Ofertas recibidas'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.line',
            'view_mode': 'list',
            'views': [(self.env.ref(
                'sipreco_purchase_preaward.purchase_order_line_preaward_list_view').id, 'list')],
            'domain': [('order_id', 'in', self.purchase_ids.ids), ('display_type', '=', False)],
            'context': {'search_default_groupby_product': 1},
        }

    def get_preaward_rows(self):
        """Rows of the sheet: the ones of the price comparison report."""
        self.ensure_one()
        return self.get_comparative_rows()

    def get_preaward_purchases(self):
        """Vendors of the sheet, oldest quotation first.

        purchase_ids comes ordered by priority and id descending, which puts
        the last vendor in the first column of the sheet.
        """
        self.ensure_one()
        return self.purchase_ids.filtered(lambda x: x.state != 'cancel').sorted('id')

    def get_preaward_items(self):
        """Preawarded line of each item, in the order of the comparison.

        An item quoted in halves by two vendors brings one entry per vendor.
        """
        self.ensure_one()
        items = []
        for row in self.get_preaward_rows():
            for quote in row['quotes'].values():
                if quote.preaward:
                    items.append({'number': row['number'], 'line': row['line'], 'quote': quote})
        return items

    def get_preaward_detail(self):
        """Preawarded lines grouped by vendor, with the amount of each one."""
        self.ensure_one()
        detail = []
        for purchase in self.get_preaward_purchases():
            lines = purchase.order_line.filtered('preaward')
            if not lines:
                continue
            detail.append({
                'purchase': purchase,
                'lines': lines,
                'amount': sum(lines.mapped('price_subtotal')),
            })
        return detail

# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    """"""

    _inherit = 'account.payment'

    # hacemos que la fecha de pago no sea obligatoria ya que seteamos fecha
    # de validacion si no estaba seteada, la setea el payment group
    payment_date = fields.Date(
        required=False,
        default=False,
    )
    assignee_id = fields.Many2one(
        'res.partner',
        'Cesionario',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        """
        Cambiamos la cuenta que usa el adelanto para utilizar aquella que
        viene de la transaccion de adelanto o del request
        """
        payment_group = self.payment_group_id
        if payment_group.transaction_with_advance_payment:
            account = payment_group.transaction_id.type_id.advance_account_id
            if not account:
                raise ValidationError(_(
                    'In payment of advance transaction type, you need to '
                    'set an advance account in transaction type!'))
            self.destination_account_id = account
        else:
            return super(
                AccountPayment, self)._compute_destination_account_id()

    @api.multi
    def confirm_check_change(self):
        self.ensure_one()
        replaced_payment_id = self._context.get('replaced_payment_id')
        if not replaced_payment_id:
            raise ValidationError(_('No replaced_payment_id on context'))
        replaced_payment = self.browse(replaced_payment_id)
        check = replaced_payment.check_id
        if check.state != 'handed':
            raise ValidationError(_(
                "Can't change check!. Check not found or check not in handed"
                " state"))
        return_payment = replaced_payment.copy({
            'payment_date': self.payment_date,
            'payment_type': 'inbound',
            'communication': _('Check Return'),
            'receiptbook_id': replaced_payment.receiptbook_id.id,
            'document_number': replaced_payment.document_number,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_in').id
        })
        return_payment.post()

        check._add_operation(
            'changed', return_payment,
            partner=return_payment.partner_id, date=return_payment.create_date)

        self.post()
        # solo reconciliamos si la cuenta es conciliable, por ej.
        # por ahora en transacciones de adelanto son no conciliables
        if self.destination_account_id.reconcile:
            (self.move_line_ids + return_payment.move_line_ids).filtered(
                lambda r: r.account_id == self.destination_account_id
            ).reconcile()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.multi
    def change_check(self):
        self.ensure_one()
        # context = self._context.copy()
        if self.check_id.state != 'handed':
            raise ValidationError(_(
                "Can't change check!. Check not found or check not in handed"
                " state"))
        context = {
            'default_payment_group_company_id': self.company_id.id,
            'default_payment_type': self.payment_type,
            'default_partner_id': self.partner_id.id,
            'default_partner_type': self.partner_type,
            'payment_group': True,
            'default_amount': self.amount,
            # 'tree_view_ref': (
            #     'account_payment_group.'
            #     'view_account_payment_from_group_tree'),
            'default_receiptbook_id': self.receiptbook_id.id,
            'default_document_number': self.document_number,
            'default_payment_group_id': self.payment_group_id.id,
            'replaced_payment_id': self.id,
        }
        return {
            'name': _('Payment Lines'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'public_budget.view_account_payment_change_check_form').id,
            'res_model': 'account.payment',
            'target': 'new',
            # 'res_id': self.id,
            'context': context,
        }

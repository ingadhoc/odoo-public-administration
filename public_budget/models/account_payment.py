from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    # hacemos que la fecha de pago no sea obligatoria ya que seteamos fecha
    # de validacion si no estaba seteada, la setea el payment group
    payment_date = fields.Date(
        required=False,
        default=False,
    )
    # para no tener que cambiar tanto el metodo get_period_payments_domain
    # agregamos este campo related
    to_signature_date = fields.Date(
        related='payment_group_id.to_signature_date',
        readonly=False,
    )
    assignee_id = fields.Many2one(
        'res.partner',
        'Cesionario',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    return_payment_id = fields.Many2one(
        'account.payment',
        string='Línea de devolución',
        readonly=True,
        help='Pago con el que este pago fue devuelto',
    )
    # En realidad la relación es o2o pero no existe en odoo
    returned_payment_ids = fields.One2many(
        'account.payment',
        'return_payment_id',
        help='Pago al que devuelve',
    )

    def write(self, vals):
        """ para pagos que son devolución no dejamos cambiar nada salvo algunos
        campos que se setean a mano
        """
        ok_fields = [
            'document_number', 'receiptbook_id', 'state', 'payment_date',
            'name', 'move_name']
        if not set(ok_fields).intersection(vals.keys()) and self.filtered(
                'returned_payment_ids'):
            raise ValidationError(_(
                'No puede modificar una devolución de retención'))
        return super(AccountPayment, self).write(vals)

    @api.depends('move_id', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        """
        Cambiamos la cuenta que usa el adelanto para utilizar aquella que
        viene de la transaccion de adelanto o del request
        """
        for rec in self:
            payment_group = rec.payment_group_id
            if payment_group.transaction_with_advance_payment:
                account = payment_group.\
                    transaction_id.type_id.advance_account_id
                if not account:
                    raise ValidationError(_(
                        'In payment of advance transaction type, you need to '
                        'set an advance account in transaction type!'))
                rec.destination_account_id = account
            elif payment_group.advance_request_id:
                rec.destination_account_id = payment_group.\
                    advance_request_id.type_id.account_id
            else:
                return super(
                    AccountPayment, rec)._compute_destination_account_id()

    def _get_liquidity_move_line_vals(self, amount):
        """
        Si es cambio de cheques recibimos clave en el contexto y hacemos
        asiento con cuenta de cheques (si no tomaria la de banco)
        """
        vals = super()._get_liquidity_move_line_vals(amount)
        if self._context.get('replaced_payment_id'):
            vals['account_id'] = self.company_id._get_check_account(
                'deferred').id
        return vals

    def confirm_check_change(self):
        #ver con jjs
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

        self.with_context(replaced_payment_id=False).post()
        # solo reconciliamos si la cuenta es conciliable, por ej.
        # por ahora en transacciones de adelanto son no conciliables
        if self.destination_account_id.reconcile:
            (self.move_line_ids + return_payment.move_line_ids).filtered(
                lambda r: r.account_id == self.destination_account_id
            ).force_full_reconcile()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def change_check(self):
        #ver con jjs
        self.ensure_one()
        # context = self._context.copy()
        if self.state == 'draft':
            check = self.create_check(
                'issue_check', 'cancel', self.check_bank_id)
            self.payment_group_id.message_post(
                body='Se anuló el cheque %s' % check.name)
            # por ahora borramos
            self.unlink()
            # borramos numero de cheque y link a cheques que se genero en paso
            # anterio
            # self.write({
            #     'check_number': False,
            #     'check_name': False,
            #     'check_ids': [(3, check.id, False)]})
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        elif self.check_id.state != 'handed':
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

    @api.onchange('check_number')
    @api.constrains('check_number')
    def unique_check_number(self):
        """
        Lo agregamos acá y no en el módulo por defecto de cheques ya que
        solo es critico por defecto que tiene varios estados intermedios antes
        de postear. De está manera lo implementamos de manera más sencilla y
        menos crítica a otros clientes.
        Solo chequeamos si hay check_number (para el caso donde se numera
        después)
        """
        # ver con jjs
        #if (self.check_type and self.check_number and
        #        (self.search([
        #            ('check_number', '=', self.check_number),
        #            ('journal_id', '=', self.journal_id.id)]) - self) or
        #        self.env['account.check'].search([
        #            ('number', '=', self.check_number),
        #            ('journal_id', '=', self.journal_id.id),
        #        ])):
        #    raise ValidationError(_(
        #        'El número de cheque %s ya se ha utilizado') % (
        #        self.check_number))

    def change_withholding(self):
        """ Arrojamos este error para recordarnos que este metodo se implementa
        en realidad en public_budget_tax_settlement porque necesitamos del
        liquidador para marcar liquidada la devolución
        """
        raise ValidationError(_('No implementado todavía'))

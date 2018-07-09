# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta


class AccountPayment(models.Model):
    """"""

    _inherit = 'account.payment'

    @api.multi
    def change_withholding(self):
        """ Este metodo se llama desde un account.payment del tipo retención
        y genera un payment group con un payment revirtiendo esa retención.
        Ya genera el pago confirmado (ya que por interfaz el usuario no puede
        confirmar pago en 0), además generamos el pago posteado para disponer
        del asiento y marcar ĺiquidada la retención original con la devolución.
        Eso mismo nos sirve para bloquear que no se puede revertir dos veces
        una misma retención.
        Lo de no poder confirmr el pago en cero bloquea que el usuario pueda
        cancelar y re-abrir el pago, ya que no lo va a poder confirmar, eso
        es deseado porque si pudiese confirmar no se haría la liquidación
        automática de la retención original
        """
        self.ensure_one()
        # por ahora implementamos solo para retenciones pero podria
        # generalizarse y usarse esta forma también para las retenciones
        if self.payment_method_code != 'withholding' and \
                self.payment_type != 'outbound':
            raise ValidationError(_(
                'El pago a cambiar debe ser una retención entregada'))

        withholding_aml = self.move_line_ids.filtered(
            lambda x: x.account_id == self.tax_withholding_id.account_id)
        if len(withholding_aml) != 1:
            raise ValidationError(_(
                'No se encontró un único apunte de retención vinculado al '
                'pago'))
        elif withholding_aml.tax_settlement_move_id:
            raise ValidationError(_(
                'No puede devolver una retención que ya fue liquidada.\n'
                '* Id Apunte de retención: %s\n'
                '* Id Asiento de liquidación: %s') % (
                    withholding_aml.id,
                    withholding_aml.tax_settlement_move_id.id))

        payment_group = self.payment_group_id.copy({
            'state': 'confirmed',
            'retencion_ganancias': 'no_aplica',
            'payment_base_date': fields.Date.today(),
            'confirmation_date': fields.Date.today(),
            'payment_date': False,
            'reference': _(
                'Devolución de retención %s') % self.withholding_number
        })
        payment_method = self.env.ref(
            'account_withholding.account_payment_method_in_withholding')
        return_payment = self.copy({
            'payment_group_id': payment_group.id,
            'payment_date': fields.Date.today(),
            'payment_method_id': payment_method.id,
            'payment_type': 'inbound',
            'withholding_number': _("Dev. Ret. %s") % self.withholding_number,
        })

        return_payment.post()
        return_aml = return_payment.move_line_ids.filtered(
            lambda x: x.account_id ==
            self.tax_withholding_id.refund_account_id)
        if len(return_aml) != 1:
            raise ValidationError(_(
                'No se encontró un único apunte de retención vinculado a la '
                'devolución'))

        # vinculamos apunte original para que quede liquidado
        withholding_aml.tax_settlement_move_id = return_aml.move_id.id
        self.payment_group_id.message_post(
            body=_('Se devolvió la retención %s con la órden de pago %s') % (
                self.withholding_number, self.display_name))
        return payment_group.get_formview_action()[0]

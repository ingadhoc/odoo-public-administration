from odoo import models, fields,  _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    def action_post(self):
        """ Si se postea un pago que es devolución entonces marcamos
        el apunte original como liquidado
        """
        res = super().action_post()
        for rec in self.filtered('returned_payment_ids'):
            return_aml = rec.line_ids.filtered(
                lambda x: x.account_id ==
                rec.tax_withholding_id.refund_repartition_line_ids.filtered(lambda x : x.repartition_type == 'tax').account_id)
            if len(return_aml) != 1:
                raise ValidationError(_(
                    'No se encontró un único apunte de retención vinculado a '
                    'la devolución'))

            # vinculamos apunte original para que quede liquidado
            if len(rec.returned_payment_ids) != 1:
                raise ValidationError(_(
                    'Se espera que el pago devuelva una y solo una retención'))

            withholding_aml = rec.returned_payment_ids.get_wihholding_aml()
            withholding_aml.tax_settlement_move_id = return_aml.move_id.id
        return res

    def get_wihholding_aml(self):
        """ Devuelve el apunte de retencion para el pago y exige que no este
        liquidado
        """
        self.ensure_one()
        withholding_aml = self.line_ids.filtered(
            lambda x: x.account_id == self.tax_withholding_id.invoice_repartition_line_ids.filtered(lambda x : x.repartition_type == 'tax').account_id)
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
        return withholding_aml

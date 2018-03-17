# -*- coding: utf-8 -*-
from openerp import models, _
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    def process_reconciliation(
            self, counterpart_aml_dicts=None, payment_aml_rec=None,
            new_aml_dicts=None):
        max_operation = self.journal_id.max_statement_operation
        if counterpart_aml_dicts:
            raise ValidationError(_(
                'No se puede pagar una deuda desde aquí. Utilice las órdenes '
                'de pago'))
        elif new_aml_dicts and max_operation:
            debit = sum([x.get('debit', 0.0) for x in new_aml_dicts])
            credit = sum([x.get('credit', 0.0) for x in new_aml_dicts])
            # for line in new_aml_dicts:
            #     if line.get('debit') > max_statement_operation or\
            #             line.get('credit') > max_statement_operation:
            if credit > max_operation or debit > max_operation:
                raise ValidationError(_(
                    'No puede hacer un registro en extractos mayor a %s'
                    ) % (max_operation))

        return super(AccountBankStatementLine, self).process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts,
            payment_aml_rec=payment_aml_rec,
            new_aml_dicts=new_aml_dicts,
        )

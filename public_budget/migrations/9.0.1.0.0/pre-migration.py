# -*- coding: utf-8 -*-
from openupgradelib import openupgrade

model_renames = [
    ('account.voucher.payment_line', 'account.payment.group.line'),
]

table_renames = [
    ('account_voucher_payment_line', 'account_payment_group_line'),
]


@openupgrade.migrate()
def migrate(cr, version):
    """
    unificamos el modulo de padron en l10n_ar_account
    """
    openupgrade.rename_models(cr, model_renames)
    openupgrade.rename_tables(cr, table_renames)

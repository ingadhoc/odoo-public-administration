# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# from odoo.api import Environment
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    """ Completamos fecha a nuevo campo:
    * tomando de payment_date si está seteado
    * tomando de confirmation_date si ya se paso a proceso de firma pero no
    tenemos payment_date
    """
    cr = env.cr

    cr.execute("""
        UPDATE account_payment_group set to_signature_date=payment_date
        WHERE payment_date is not null
    """)

    cr.execute("""
        UPDATE account_payment_group set to_signature_date=confirmation_date
        WHERE payment_date is null and state in
        ('signature_process', 'signed', 'posted')
    """)

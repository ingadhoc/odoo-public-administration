# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# from openerp.api import Environment
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    """
    NOTA en realidad esto debería haber sido en un pre-upgrade para que
    odoo no los actualice en esta misma actualización
    """
    cr = env.cr

    cr.execute("""
        UPDATE ir_model_data set noupdate=True
        WHERE name in (
            'action_aeroo_advance_request_debt_report',
            'action_aeroo_report_advance_request',
            'action_aeroo_report_advance_return',
            'action_aeroo_report_asset',
            'action_aeroo_report_budget',
            'action_aeroo_report_check',
            'action_aeroo_report_liquidation',
            'action_aeroo_report_payment_order_list_checks',
            'action_aeroo_report_payment',
            'action_aeroo_report_payment_receipt',
            'action_aeroo_report_remit',
            'sipreco_stylesheet',
            'action_aeroo_report_transaction') and module = 'public_budget'
    """)

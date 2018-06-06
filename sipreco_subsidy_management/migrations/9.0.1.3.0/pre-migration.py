# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# from openerp.api import Environment
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr

    cr.execute("""
        UPDATE ir_model_data set noupdate=True
        WHERE name in (
            'action_aeroo_subsidy_resolution_report',
            'action_aeroo_subsidy_resolution_INSTIT',
            'action_aeroo_subsidy_resolution_ITRANS_report',
            'action_aeroo_subsidy_resolution_COMUN_report',
            ) and module = 'sipreco_subsidy_management'
    """)

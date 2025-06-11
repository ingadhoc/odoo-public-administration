# -*- coding: utf-8 -*-
import logging

from odoo import api, models


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @api.model
    def _get_demo_data(self, company=False):
        demo_data = super()._get_demo_data(company)
        if company in (
            self.env.ref('public_budget.company_sipreco', raise_if_not_found=False),
        ):
            return {}
            # Do not load generic demo data on these companies
        return demo_data

    def _post_load_demo_data(self, company=False):
        if company not in (
            self.env.ref('public_budget.company_sipreco', raise_if_not_found=False),
        ):
            # Do not load generic demo data on these companies
            return super()._post_load_demo_data(company)

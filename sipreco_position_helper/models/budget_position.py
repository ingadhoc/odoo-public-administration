# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BudgetPosition(models.Model):

    _inherit = 'public_budget.budget_position'

    individual_code = fields.Char(
        # lo hacemos no requerido para no tener warnings, no es lo mas elegante
        # pero funciona, requerido por vista..
        required=False,
    )
    code = fields.Char(
        compute='_compute_code',
        store=True,
        required=False,
    )

    @api.multi
    @api.depends(
        'individual_code',
        'parent_id.individual_code',
    )
    def _compute_code(self):
        for rec in self:
            rec.code = "%s%s" % (
                rec.parent_id.code or '',
                rec.individual_code or '')

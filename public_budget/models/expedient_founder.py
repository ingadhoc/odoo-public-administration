# -*- coding: utf-8 -*-
from odoo import models, fields


class ExpedientFounder(models.Model):

    _name = 'public_budget.expedient_founder'
    _description = 'Expedient Founder'

    name = fields.Char(
        required=True
    )

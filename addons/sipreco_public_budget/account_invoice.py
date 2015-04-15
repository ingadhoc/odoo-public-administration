# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import Warning


class account_invoice(models.Model):
    _inherit = "account.invoice"

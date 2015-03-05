# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class partner(models.Model):
    """"""

    _inherit = 'res.partner'

    subsidy_recipient = fields.Boolean(
        'Subsidy Recipient',
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

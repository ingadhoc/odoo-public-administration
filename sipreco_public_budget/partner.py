# -*- coding: utf-8 -*-
from openerp import models, fields


class partner(models.Model):
    """"""

    _inherit = 'res.partner'

    subsidy_recipient = fields.Boolean(
        'Subsidy Recipient',
        )
    # Make some fields require
    responsability_id = fields.Many2one(
        required=True,
        )
    document_type_id = fields.Many2one(
        required=True,
        )
    document_number = fields.Char(
        required=True,
        )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

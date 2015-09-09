# -*- coding: utf-8 -*-
from openerp import models, api
from lxml import etree


class definitive_line(models.Model):

    _inherit = 'public_budget.definitive_line'

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form', toolbar=False,
            submenu=False):
        result = super(definitive_line, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        definitive_partner_type = self._context.get('definitive_partner_type')
        if definitive_partner_type == 'subsidy_recipient':
            doc = etree.XML(result['arch'])
            node = doc.xpath("//field[@name='supplier_id']")[0]
            node.set('domain', "[('subsidy_recipient', '=', True)]")
            result['arch'] = etree.tostring(doc)
        return result

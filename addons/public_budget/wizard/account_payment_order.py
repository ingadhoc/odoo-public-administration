# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.tools.translate import _


class payment_order_create(osv.osv_memory):

    """
    Modificay payment_order_create ..
    """

    _inherit = 'payment.order.create'

    def search_entries(self, cr, uid, ids, context=None):
        payment = self.pool.get('payment.order').browse(cr, uid, context[
            'active_id'], context=context)
        if not payment.transaction_id:
            return super(payment_order_create, self).search_entries(
                cr, uid, ids, context)
        line_obj = self.pool.get('account.move.line')
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        search_due_date = data.duedate

        # Search for move line to pay:
        # if payment.transaction_id then we search only dues for invoices of
        # this transaction id
        domain = [
            ('reconcile_id', '=', False),
            ('account_id.type', '=', 'payable'),
            ('credit', '>', 0),
            ('invoice.transaction_id', '=', payment.transaction_id.id),
            ('account_id.reconcile', '=', True)]
        domain = domain + [
            '|', ('date_maturity', '<=', search_due_date),
            ('date_maturity', '=', False)]
        line_ids = line_obj.search(cr, uid, domain, context=context)
        context = dict(context, line_ids=line_ids)
        model_data_ids = mod_obj.search(
            cr, uid, [('model', '=', 'ir.ui.view'),
                      ('name', '=', 'view_create_payment_order_lines')],
            context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=[
            'res_id'], context=context)[0]['res_id']
        return {'name': _('Entry Lines'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payment.order.create',
                'views': [(resource_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

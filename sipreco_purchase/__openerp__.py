# -*- coding: utf-8 -*-
{
    'author': 'ADHOC SA,Odoo Community Association (OCA)',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'data': [
        'views/stock_move_view.xml',
        'views/stock_picking_type_view.xml',
        'views/stock_picking_view.xml',
        'views/purchase_requisition_view.xml',
    ],
    'demo': [
        'demo/stock_demo.xml',
    ],
    'depends': [
        'public_budget',
        'purchase_requisition',
        # 'stock_procurement_request',
    ],
    'installable': True,
    'name': 'Sipreco Purchase Management',
    'test': [],
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
}

# -*- coding: utf-8 -*-
{
    'author': 'ADHOC SA,Odoo Community Association (OCA)',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'data': [
        'data/ir_actions_server_data.xml',
        'views/stock_move_view.xml',
        'views/stock_picking_type_view.xml',
        'views/stock_picking_view.xml',
        'views/purchase_requisition_view.xml',
        'security/sipreco_purchase_security.xml',
        'security/hide_groups.xml',
    ],
    'demo': [
        'demo/stock_demo.xml',
        'demo/res_users_demo.xml',
    ],
    'depends': [
        'public_budget',
        'purchase_requisition',
        'stock_procurement_request',
    ],
    'installable': True,
    'name': 'Sipreco Purchase Management',
    'test': [],
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
}

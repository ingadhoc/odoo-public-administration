{
    'name': 'Sipreco Purchase Management',
    'version': '11.0.1.15.0',
    'license': 'AGPL-3',
    'author': 'ADHOC SA,Odoo Community Association (OCA)',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'depends': [
        'public_budget',
        'purchase_requisition',
        'stock_ux',
        'stock_request_ux',
    ],
    'data': [
        'data/ir_actions_server_data.xml',
        'data/sequence_data.xml',
        'security/sipreco_purchase_security.xml',
        'security/hide_groups.xml',
        'security/ir.model.access.csv',
        'views/stock_move_views.xml',
        'views/stock_move_line_views.xml',
        'views/stock_picking_type_views.xml',
        'views/stock_picking_views.xml',
        'views/purchase_requisition_views.xml',
        'views/purchase_requisition_type_views.xml',
        'views/stock_request_order_views.xml',
        'views/stock_request_views.xml',
        'views/res_users_views.xml',
        'views/stock_location_route_views.xml',
        'views/product_template_views.xml',
        'views/purchase_order_views.xml',
        'views/transaction_views.xml',
        'views/stock_inventory_views.xml',
        'reports/purchase_requisition_report.xml',
        'reports/purchase_order_publicity_report.xml',
        'wizards/create_expedients_wizard_views.xml',
    ],
    'demo': [
        'demo/stock_demo.xml',
        'demo/res_users_demo.xml',
        'demo/product_demo.xml',
        'demo/sequence_demo.xml',
    ],
    'installable': True,
}

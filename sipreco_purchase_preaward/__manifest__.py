{
    'name': 'Sipreco Purchase Preaward',
    'version': '18.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'category': 'Purchase',
    'summary': 'Preadjudicación de Solicitudes de Compra publicadas en la web',
    'depends': [
        'sipreco_purchase_web',
    ],
    'data': [
        'views/purchase_order_views.xml',
        'views/purchase_requisition_views.xml',
        'reports/purchase_requisition_preaward_report.xml',
        'reports/purchase_requisition_preaward_templates.xml',
    ],
    'installable': True,
    'application': False,
}

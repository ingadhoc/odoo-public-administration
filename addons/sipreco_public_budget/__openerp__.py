# -*- coding: utf-8 -*-
{'active': False,
    'author':  'Ingenieria ADHOC',
    'website': 'www.ingadhoc.com',
    'category': 'Accounting & Finance',
    'data': [
        'wizard/transaction_definitive_make_invoice_view.xml',
        'views/res_partner_view.xml',
        'views/custom_views.xml',
        'views/account_asset_view.xml',
        'security/security.xml',
    ],
    'demo': [],
    'depends': [
        'l10n_ar_invoice',
        'public_budget',
        'account_asset',
        'share',
    ],
    'description': '''
Public Budget Sipreco Customizations
====================================
* Agregar punto de venta y numero de factura en wizar de generacion de factura
''',
    'installable': True,
    'name': 'Public Budget Sipreco Customizations',
    'test': [],
    'version': '1.243'}

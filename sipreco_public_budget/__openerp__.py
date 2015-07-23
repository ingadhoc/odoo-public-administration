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
        'views/account_voucher_view.xml',
        'views/account_check_view.xml',
        'workflow/account_voucher_workflow.xml',
        'workflow/account_check_workflow.xml',
        'security/security.xml',
        'data/data.xml',
        'reports/receipt_report.xml',
    ],
    'demo': [],
    'depends': [
        'l10n_ar_invoice',
        'l10n_ar_aeroo_voucher',
        'public_budget',
        'account_asset',
        'share',
        'web_m2x_options',
        'account_voucher_double_validation',
        'account_tax_settlement_withholding',
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

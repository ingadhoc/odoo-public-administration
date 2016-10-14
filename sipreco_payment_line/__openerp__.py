# -*- coding: utf-8 -*-
{
    'active': False,
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'data': [
        'wizards/account_voucher_payment_line_import_view.xml',
        'views/account_voucher_view.xml',
        'views/res_partner_bank_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'depends': [
        'public_budget',
    ],
    'description': '''
Sipreco Payment Lines
=====================
Add payment lines on vouchers
''',
    'installable': True,
    'name': 'Sipreco Payment Lines',
    'test': [],
    'version': '8.0.1.0.0'}

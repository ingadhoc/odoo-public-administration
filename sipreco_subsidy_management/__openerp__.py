# -*- coding: utf-8 -*-
{'active': False,
    'author':  'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'data': [
        'views/subsidy_view.xml',
        'views/transaction_type_view.xml',
        'views/approval_arrangement_view.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
    ],
    'demo': [
        'demo/public_budget.transaction_type.csv',
        'demo/subsidy_demo.xml',
    ],
    'depends': [
        'sipreco_public_budget',
    ],
    'description': '''
Public Budget Subsidy Management
================================
''',
    'installable': True,
    'name': 'Public Budget Subsidy Management',
    'test': [],
    'version': '8.0.0.0.0'}

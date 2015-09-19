# -*- coding: utf-8 -*-
{
    'name': 'Sipreco Set Up Data CMD',
    'version': '8.0.0.0.0',
    'category': 'Accounting',
    'sequence': 14,
    'summary': '',
    'description': """
Sipreco Set Up Data TMC
=======================
    """,
    'author':  'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'images': [
    ],
    'depends': [
        'sipreco_public_budget',
        'l10n_ar_bank',
        'l10n_ar_states',
    ],
    'data': [
        'data/location.xml',
        'data/budget_position.xml',
        'data/res_company.xml',
        'data/res_users.xml',
        'data/account_account.xml',
        'data/account_journal.xml',
        'reports/payment_order_report.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

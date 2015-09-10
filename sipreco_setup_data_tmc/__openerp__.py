# -*- coding: utf-8 -*-
{
    'name': 'Sipreco Set Up Data TMC',
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
    ],
    'data': [
        'data/account/account_period.xml',
        'data/account.journal.csv',
        'data/users/res.partner.csv',
        'data/users/admin_user/res.users.csv',
        'data/users/res.users.csv',
        'data/res.partner.bank.csv',
        'data/account.tax.withholding.csv',
        'data/public_budget.budget_position.csv',
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

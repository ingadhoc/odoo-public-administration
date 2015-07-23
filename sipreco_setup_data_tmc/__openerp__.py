# -*- coding: utf-8 -*-
{
    'name': 'Sipreco Set Up Data TMC',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 14,
    'summary': '',
    'description': """
Sipreco Set Up Data TMC
=======================
    """,
    'author':  'Ingenieria ADHOC',
    'website': 'www.ingadhoc.com',
    'images': [
    ],
    'depends': [
        'sipreco_account_chart',
        'sipreco_public_budget',
        'account_check',
        'l10n_ar_bank',
        # 'l10n_ar_invoice',
        'account_tax_settlement_voucher',
        # 'account_balance_constraint',
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
    'installable': False,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

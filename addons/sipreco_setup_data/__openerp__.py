# -*- coding: utf-8 -*-
{
    'name': 'Sipreco Set Up Data',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 14,
    'summary': '',
    'description': """
Sipreco Set Up Data
===================
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
        'l10n_ar_invoice',
    ],
    'data': [
        'data/account/ir.sequence.csv',
        'data/res.company.csv',
        # datos demo
        'demo/account/account_period.xml',
        'demo/account.journal.csv',
        'demo/journal_data.xml',
        'demo/res.partner.csv',
        'demo/users/res.partner.csv',
        'demo/users/res.users.csv',
        'demo/res.partner.bank.csv',
        'demo/public_budget.expedient_founder.csv',
        'demo/public_budget.expedient_category.csv',
        'demo/public_budget.location.csv',
        'demo/public_budget.expedient.csv',
        'demo/public_budget.budget_position_category.csv',
        'demo/public_budget.budget_pos_exc_rest.csv',
        'demo/public_budget.budget_position.csv',
        'demo/public_budget.budget.csv',
        'demo/public_budget_demo.xml',
        'demo/public_budget.budget_detail.csv',
        'demo/public_budget.transaction_type.csv',
        'demo/public_budget.transaction.csv',
        'demo/public_budget.preventive_line.csv',
        'demo/public_budget.definitive_line.csv',
        'demo/res_users.xml',
        'demo/public_budget.remit.csv',
        'demo/public_budget.budget_modification.csv',
        'demo/public_budget.budget_modification_detail.csv',
        # 'demo/account.asset.asset.csv', hay que crear antes la categoria de asset
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

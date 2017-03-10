# -*- coding: utf-8 -*-
{
    'name': 'Sipreco Set Up Data CMR',
    'version': '9.0.1.0.0',
    'category': 'Accounting',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'images': [
    ],
    'depends': [
        'sipreco_public_budget',
        'l10n_ar_bank',
        'l10n_ar_states',
        'l10n_ar_afipws_fe',
        # for no reload on check on afip
        'web_ir_actions_act_window_none',
    ],
    'data': [
        'data/location.xml',
        'data/budget_position.xml',
        'data/res_company.xml',
        'data/res_employees.xml',
        'data/res_users.xml',
        'data/account_account.xml',
        'data/account_journal.xml',
        'reports/payment_order_report.xml',
        'reports/payment_receipt_report.xml',
        'reports/remit_report_subsidy.xml',
        'reports/payment_order_cmd_list.xml',
        'reports/payment_order_cmd_multi.xml',
        'reports/stylesheet.xml',
        'reports/check_report.xml',
        'views/check_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': False,
    'auto_install': False,
    'application': False,
}

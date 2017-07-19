# -*- coding: utf-8 -*-
{
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'data': [
        'reports/subsidy_note_report.xml',
        'reports/subsidy_approval_arrangement_report.xml',
        'reports/remit_report_subsidy.xml',
        'reports/subsidy_form_report.xml',
        'reports/subsidy_report.xml',
        'views/subsidy_view.xml',
        'views/transaction_type_view.xml',
        'views/subsidy_approval_arrangement_view.xml',
        'views/subsidy_note_type_view.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/subsidy_note_type_data.xml',
    ],
    'demo': [
        'demo/public_budget.transaction_type.csv',
        'demo/subsidy_demo.xml',
    ],
    'depends': [
        'public_budget',
    ],
    'installable': True,
    'name': 'Public Budget Subsidy Management',
    'test': [],
    'version': '9.0.1.0.0',
}

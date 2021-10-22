{
    'name': 'Public Budget Subsidy Management',
    'version': '13.0.1.2.0',
    'author': 'ADHOC SA,Odoo Community Association (OCA)',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'data': [
        'reports/subsidy_note_report.xml',
        'reports/subsidy_approval_arrangement_report.xml',
        'reports/remit_report_subsidy.xml',
        'reports/subsidy_form_report.xml',
        'reports/subsidy_report.xml',
        'reports/subsidy_report_resolution.xml',
        'views/subsidy_views.xml',
        'views/transaction_type_views.xml',
        'views/subsidy_approval_arrangement_views.xml',
        'views/subsidy_note_type_views.xml',
        'views/subsidy_resolution_views.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/subsidy_note_type_data.xml',
        'data/cron.xml',
    ],
    'demo': [
        'demo/public_budget.transaction_type.csv',
        'demo/subsidy_demo.xml',
    ],
    'depends': [
        'public_budget',
    ],
    'installable': False,
}

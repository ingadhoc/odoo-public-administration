{
    'name': 'Public Budget Subsidy Management',
    'version': "15.0.1.0.0",
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
<<<<<<< HEAD
||||||| parent of bec37d4 (temp)
        'data/ir_actions_server_data.xml',
        'wizards/create_expedients_wizard_views.xml',
        'views/expedient_views.xml'
=======
        'data/ir_actions_server_data.xml',
        'wizards/create_administrative_process_wizard_views.xml',
        'views/expedient_views.xml'
>>>>>>> bec37d4 (temp)
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

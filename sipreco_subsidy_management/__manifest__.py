{
    'name': 'Public Budget Subsidy Management',
    'version': "15.0.1.1.0",
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
        'reports/report_ticket_template.xml',
        'views/subsidy_views.xml',
        'views/subsidy_ticket_views.xml',
        'views/transaction_type_views.xml',
        'views/subsidy_approval_arrangement_views.xml',
        'views/subsidy_note_type_views.xml',
        'views/subsidy_resolution_views.xml',
        'views/subsidy_ticket_director_views.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/subsidy_note_type_data.xml',
        'data/cron.xml',
        'data/ir_actions_server_data.xml',
        'wizards/create_expedients_wizard_views.xml',
        'views/expedient_views.xml'
    ],
    'demo': [
        'demo/public_budget.transaction_type.csv',
        'demo/subsidy_demo.xml',
        'demo/helpdesk_demo.xml',
    ],
    'depends': [
        'public_budget',
        'helpdesk'
    ],
    'installable': False,
}

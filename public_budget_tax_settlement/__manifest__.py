{
    'name': 'Public Budget integration with Tax settlement',
    'version': '11.0.1.0.0',
    'author': 'ADHOC SA,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'data': [
        'views/account_journal_dashboard_views.xml',
        'views/account_move_views.xml',
        'views/account_move_line_views.xml',
    ],
    'demo': [
    ],
    'depends': [
        'public_budget',
        'account_tax_settlement',
    ],
    'installable': False,
    'auto_install': True,
}

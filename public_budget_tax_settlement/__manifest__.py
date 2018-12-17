{
    'author': 'ADHOC SA,Odoo Community Association (OCA)',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'data': [
        'views/account_journal_dashboard_view.xml',
        'views/account_move_view.xml',
        'views/account_move_line_view.xml',
    ],
    'demo': [
    ],
    'depends': [
        'public_budget',
        'account_tax_settlement',
    ],
    'installable': False,
    'auto_install': True,
    'name': 'Public Budget integration with Tax settlement',
    'version': '9.0.1.2.0',
    'license': 'AGPL-3',
}

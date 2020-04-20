{
    'name': 'Sipreco Payment Lines',
    'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ADHOC SA,Odoo Community Association (OCA)',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'depends': [
        'public_budget',
    ],
    'data': [
        'wizards/account_payment_group_line_import_views.xml',
        'views/account_payment_group_views.xml',
        'views/res_partner_bank_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
}

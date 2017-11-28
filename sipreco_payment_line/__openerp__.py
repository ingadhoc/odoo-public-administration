# -*- coding: utf-8 -*-
{
    'author': 'ADHOC SA,Odoo Community Association (OCA)',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'data': [
        'wizards/account_payment_group_line_import_view.xml',
        'views/account_payment_group_view.xml',
        'views/res_partner_bank_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'depends': [
        'public_budget',
    ],
    'installable': True,
    'name': 'Sipreco Payment Lines',
    'test': [],
    'version': '9.0.1.0.0',
}

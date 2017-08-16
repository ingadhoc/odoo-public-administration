# -*- coding: utf-8 -*-
{
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'category': 'Accounting & Finance',
    'data': [
        'wizards/account_voucher_payment_line_import_view.xml',
        'views/account_payment_group_view.xml',
        'views/res_partner_bank_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'depends': [
        'public_budget',
    ],
    # TODO todavia no lo activamos porque tal vez lo sacamos fuera de sipreco
    'installable': False,
    'name': 'Sipreco Payment Lines',
    'test': [],
    'version': '9.0.1.0.0',
}

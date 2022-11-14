{
    'name': 'Sipreco Project',
    'license': 'LGPL-3',
    'version': "15.0.1.0.0",
    'category': 'Accounting',
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA,Odoo Community Association (OCA)',
    'website': 'www.adhoc.com.ar',
    'images': [
    ],
    'depends': [
        'web_m2x_options',
        'public_budget',
        'account_accountant',
        'l10n_ar_bank',
        # 'web_pdf_preview',
        'account_tax_settlement',
        'account_reports',
        # para que genere los diarios que queremos
        # 'portal',  # necesitamos portal por un error
        #  raro al crear un voucher
        #  es un error de javascript pero con portal de
        #  alguna manera se
        #  resuelve. Luego de instalar portal refrescar pantalla
    ],
    'data': [
        'data/ir_parameters.xml',
    ],
    'demo': [
        'demo/config_data.xml',
        'demo/load_es_lang.xml',
    ],
    'installable': False,
    'auto_install': False,
    'application': True,
}

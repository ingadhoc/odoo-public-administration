# -*- coding: utf-8 -*-
{
    'name': 'Sipreco Project',
    'version': '9.0.1.0.0',
    'category': 'Accounting',
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'images': [
    ],
    'depends': [
        # # 'sipreco_account_chart',
        # 'account_move_line_no_filter',
        # 'sipreco_public_budget',
        'public_budget',
        'l10n_ar_account_withholding',
        # 'web_sheet_full_width',
        # 'account_partner_balance',
        # 'account_cancel',
        # 'account_voucher_multic_fix',
        # 'account_multic_fix',
        # 'admin_technical_features',
        # 'account_accountant',
        # 'account_clean_cancelled_invoice_number',
        # 'l10n_ar_bank',
        # 'account_transfer',
        # 'account_statement_disable_invoice_import',
        # 'account_voucher_popup_print',
        # 'account_balance_constraint',
        # 'base_state_active',
        # 'partner_vat_unique',
        # # por alguna razon no lo instala, ver con juan
        # 'portal',  # necesitamos portal por un error raro al crear un voucher
        # # es un error de javascript pero con portal de alguna manera se
        # # resuelve. Luego de instalar portal refrescar pantalla
        # 'disable_openerp_online',
        # 'web_export_view',
    ],
    'data': [
        'data/ir_parameters.xml',
    ],
    'demo': [
        'demo/config_data.xml',
        'demo/load_es_lang.yml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

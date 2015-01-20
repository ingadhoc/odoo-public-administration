# -*- coding: utf-8 -*-
{
    'name': 'Sipreco Set Up Data',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 14,
    'summary': '',
    'description': """
Sipreco Set Up Data
===================
# 01 - Pasos alta BD Sipreco
# =============================
# Cambiar formato de fecha en lenguaje Español
# Importar archivo es_AR.po, en carpeta sipreco_set_up_data > l18i
# Nombre de idioma: Cualquier texto
# Código: es_AR
# Archivo: es_AR.po
# Sobreescribir terminos: True
# En el diario de compras y abono de compras marcar "use documents" y en la pestaña documentos correr el wizard de configuración
# En proveedores, establecer por defecto que tomen cuenta Proveedores como Cuenta a Pagar
    """,
    'author':  'Ingenieria ADHOC',
    'website': 'www.ingadhoc.com',
    'images': [
    ],
    'depends': [
        'sipreco_account_chart',
        'sipreco_custom_views',
        'sipreco_public_budget',
        'account_cancel',
        'account_bank_voucher',
        'account_accountant',
        'contacts',
        'account_clean_cancelled_invoice_number',
        'account_check',
        'l10n_ar_bank',
    ],
    'data': [
        'data/account/ir.sequence.csv'
    ],
    'demo': [
        'demo/journal_data.xml',
        'demo/res.partner.csv',
        'demo/users/res.partner.csv',
        'demo/users/res.users.csv',
        'demo/account.journal.csv',
        'demo/res.partner.bank.csv',
        'demo/payment.mode.csv',
        'demo/public_budget.expedient_founder.csv',
        'demo/public_budget.expedient_category.csv',
        'demo/public_budget.expedient.csv',
        'demo/public_budget.budget_position_category.csv',
        'demo/public_budget.budget_pos_exc_rest.csv',
        'demo/public_budget.budget_position.csv',
        'demo/public_budget.budget.csv',
        'demo/public_budget_demo.xml',
        'demo/public_budget.budget_detail.csv',
        'demo/public_budget.transaction_type.csv',
        'demo/public_budget.transaction.csv',
        'demo/public_budget.preventive_line.csv',
        'demo/public_budget.definitive_line.csv',
        'demo/res_users.xml',
        'demo/public_budget.location.csv',
        'demo/public_budget.expedient_move.csv',
        'demo/demo_data.xml',
        'demo/public_budget.budget_modification.csv',
        'demo/public_budget.budget_modification_detail.csv',
        'demo/account.asset.asset.csv',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

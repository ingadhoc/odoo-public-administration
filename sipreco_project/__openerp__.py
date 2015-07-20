# -*- coding: utf-8 -*-
{
    'name': 'Sipreco Project',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 14,
    'summary': '',
    'description': """
Sipreco Project
===============
Installs All Sipreco Project Dependencies
# 01 - Pasos alta BD Sipreco
# =============================
# Cambiar formato del separador por "[3,3,1]", cambiar separador decimales por "," y de miles por "."
# Establecer por defecto en Proveedores: Tipo de documento = CUIT, Ciudad: Rosario
# Importar archivo es_AR.po, en carpeta sipreco_set_up_data > l18i
# Nombre de idioma: Cualquier texto
# Código: es_AR
# Archivo: es_AR.po
# Sobreescribir terminos: True
# En el diario de compras y abono de compras marcar "use documents" y en la pestaña documentos correr el wizard de configuración
# En proveedores, establecer por defecto que tomen cuenta Proveedores como Cuenta a Pagar
    """,
    'author':  'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'images': [
    ],
    'depends': [
        'sipreco_account_chart',
        'sipreco_public_budget',
        'account_cancel',
        'admin_technical_features',
        'account_bank_voucher',
        'account_accountant',
        'account_clean_cancelled_invoice_number',
        'l10n_ar_bank',
        'portal',   # necesitamos portal por un error raro al crear un voucher
        # es un error de javascript pero con portal de alguna manera se
        # resuelve. Luego de instalar portal refrescar pantalla
        'disable_openerp_online',
    ],
    'data': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

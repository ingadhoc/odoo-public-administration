# -*- coding: utf-8 -*-
{
    'name': 'Sipreco Project',
    'version': '8.0.0.0.0',
    'category': 'Accounting',
    'sequence': 14,
    'summary': '',
    'description': """
Sipreco Project
===============
Modulos principales del proyecto:
---------------------------------
* Sipreco Project: Instala todos los modulos del proyecto
* Sipreco Chart Accunt: Plan contable del proyecto Sipreco
* Sipreco Public Budget: Customizaciones a public budget para el proyecto Sipreco
* Sipreco Setup Data TMC: Carga de datos iniciales para el proyecto Sipreco/TMC
* Sipreco Setup Data CMD: Carga de datos iniciales para el proyecto Sipreco/CMD

# 01 - Pasos alta BD Sipreco
=============================
# Cambiar formato del separador por "[3,3,1]", cambiar separador decimales por "," y de miles por "."
# Establecer por defecto en Proveedores: Tipo de documento = CUIT, Ciudad: Rosario
# Importar archivo es_AR.po, en carpeta sipreco_set_up_data > l18i
# Nombre de idioma: Cualquier texto
# Código: es_AR
# Archivo: es_AR.po
# Sobreescribir terminos: True
# En el diario de compras y abono de compras marcar "use documents" y en la pestaña documentos correr el wizard de configuración
# En proveedores, establecer por defecto que tomen cuenta Proveedores como Cuenta a Pagar
# Restringir balance en cuentas contables correspondientes a medios de pago (Transferencias bancarias). Fijar monto 0.0 (evita giros en descubierto)

    """,
    'author':  'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'images': [
    ],
    'depends': [
        # 'sipreco_account_chart',
        'account_move_line_no_filter',
        'sipreco_public_budget',
        'account_cancel',
        'account_voucher_multic_fix',   
        'account_multic_fix',
        'admin_technical_features',
        'account_accountant',
        'account_clean_cancelled_invoice_number',
        'l10n_ar_bank',
        'account_transfer',
        'account_statement_disable_invoice_import',
        'account_voucher_popup_print',
        'account_balance_constraint',
        'partner_vat_unique',
        # por alguna razon no lo instala, ver con juan
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

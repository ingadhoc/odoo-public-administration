.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===============
Sipreco Project
===============

MODULO PARA DEMO Y DEPENDENCIAS


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

Installation
============

To install this module, you need to:

#. Only need to install the module

Configuration
=============

To configure this module, you need to:

#. Nothing to configure

Usage
=====

To use this module, you need to:

#. Go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: http://runbot.adhoc.com.ar/

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/odoo-public-administration/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* |company| |icon|

Contributors
------------

Maintainer
----------

|company_logo|

This module is maintained by the |company|.

To contribute to this module, please visit https://www.adhoc.com.ar.

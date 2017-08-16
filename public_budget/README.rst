.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============
Public Budget
=============

Modulo generico para gestion publica presupuestaria/contable.

Datos demo:
* Compañía a utilizar: SIPRECO
* Usuarios disponibles (clave igual a usuario):

    * admin: lo ideal es no usarlo ya que ve todas las compañías y saltea restricciones
    * demo: director de habilitaciones, contaduria y secretaria y con configuración, ideal para hacer pruebas en vez de usar admin.
    * portal_expedientes: usuario portal para trabajar con expedientes
    * portal: usuario portal todavía no implementado (en el futuro para proveedores por ejemplo)
    * habilitaciones_manager: director de habilitaciones
    * habilitaciones_user: usuario de habilitaciones
    * contaduria_manager: director de contaduria
    * contaduria_user: usuario de contaduria
    * secretaria_manager: director de secretaria
    * secretaria_user: usuario de secretaria
    * general: usuario solo empleado, no debería poder hacer nada, por ahora no tienen ningún uso

Algunas observaciones de uso/desarrollo
=======================================

#. Cheques:
  * Los cheques se generan cuando se valida el pago, en ese momento queda como entregado y afecta la cuenta de "cheques diferidos". (ESTO NO VA MAS ASI) cuando lo entregan físicamente marcan el débito, en ese momento registramos la salida del banco.

                HOY:                    V9
Validar Pago
                Cheque a entregar       entregado               Entregado
                Salió de Banco          Valores diferidos     

Entrega física
                cheque entregado        Debitado
                Banco a Banco           Dif a banco


La altenetiva que elegimos es hacer que la validación del pago se haga con la entrega física, luego cuando se identifica el débito, se registra como debitado. 
Desventajas/observaciones:
* hasta que no se entregue el cheque no existe
* si hay más de un cheque en un pago, no se pueden "entregar" individualmente (tendrán que hacer muchos pagos)
* haŕía que hacer un poka joke para que no se olviden de validar el pago al entregar

Si llegan a necesitar si o si hacer el débito directo, podemos automatizar que al validar el pago se debiten los cheques.

#. Subsidios:
  * La fecha del cargo se calcula en función a todos los pagos vinculados en los cuales se agrego un campo fecha del cargo.
  * la fecha del cargo en los pagos se calcula como siemrpe que el pago este validado (posted) y según:
    * si no tiene cheques: se usa la fecha de pago
    * si tiene cheques: se suma solamente si fue debitado (cuando ellos lo entregan fisicamente) y se usa la fecha de débito

Installation
============

To install this module, you need to:

#. Do this ...

Configuration
=============

To configure this module, you need to:

#. Go to ...

Usage
=====

To use this module, you need to:

#. Go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.adhoc.com.ar/

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* ADHOC SA: `Icon <http://fotos.subefotos.com/83fed853c1e15a8023b86b2b22d6145bo.png>`_.

Contributors
------------


Maintainer
----------

.. image:: http://fotos.subefotos.com/83fed853c1e15a8023b86b2b22d6145bo.png
   :alt: Odoo Community Association
   :target: https://www.adhoc.com.ar

This module is maintained by the ADHOC SA.

To contribute to this module, please visit https://www.adhoc.com.ar.

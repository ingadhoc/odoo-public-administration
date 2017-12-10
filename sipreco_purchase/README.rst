.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Sipreco Purchase Management
===========================

Datos demo:
  * Usuarios (entre paréntesis grupo principal):
    * requirente / requirente (Compras / Requirente: group_requester)
    * solicitante_economato / solicitante_economato (Compras / Solicitante: stock.group_stock_user)
    * solicitante_informatica / solicitante_informatica (idem anterior)
    * comprador / comprador (Compras / Comprador: purchase.group_purchase_user)
    * secretario / secretario (Aprobar Solicitudes de Compra (hereda solicitante): group_approve_purhcase_req)
  * Productos:
    * Informatica
    * Economato 1
    * Economato 2

LISTO:
* Permitir a Unidad dde compra generar solicitudes de compra
* Obligar definir unidad de compra en requerimiento y limiar a que solo productos de esa Ude compra y agrego datos demo secretaría administrativa, secret. paramentaria
* en datos demo poner productos como consumubles para evitar problemas con reserva y demas (y ponerlo tipo para tec features en productos)
* renombrar licitaciones de compra a solicitudes de compra
* que si se cancela un purchase.req se cancelen los proc.order (si secretario cancela solicitud de compra se cancelan los requerimientos vinculados)
* Permisos
  Compras y Abastecimientos:
      Requirente
      Solicitante
          Generar el purchase requisition
          Entrega mercaderia
      Comprador
          Unir
  Secreateria manager:
      aprobar el purchase requisition
* No filtrar en Purchase requisition, por defecto, el usuario comprador.
* Poner por defecto el menu Purchase Requisition en modulo compras (oculté el resto por ahora, si los necesitamos los agregamos)
* Vincular en Purchase Requisition
  - Tramite Administrativo (Expediente)
  - Transacciones que tengan ese expediente
  * Requirente, un usuario individual, no se puede alterar el partner en el Pedido de Abastecimiento (para que no pida uno por otro)
* En el Requerimiento de abastecimiento, llevar el costo del producto, para los productos que usualmente se piden, sirve como valor ya fijado, en los productos varios o esporadicos, el requirente, lo puede setear (no modifica el costo del producto en el maestro), para dar valor estimado
* Geerar tipos de solitud de compra demo "Compra directa, concurso de precios.." (al final me confundí, no existía un tipo de solicitud de compra en odoo, creo que está en v11 recién, asi que por ahora use los tipo de transacción como me habías dicho)
* Que sel requerimiento esta likeado a solicitud de compra, mostrar el link (nomas que se sepa que está, no lo puede ver) 
* Sacar boton de facturas en ordenes de compra
* Agregar campo notas en Pedido de Abastecimiento, para poner Motivacion de compra (no obligatorio) (y que viaje a líneas de compra)
* A comprador no le permite confirmar orden de compra


TODO:
* Compras tiene que poder unir las solicitudes de compra en una sola solicitud, con los numeros de solicitud concatenados
* agregar campo tramite administrativo pero solo si ya se aprobó la solicitud. (No permite cargar Tramite Administrativo en solicitud, hasta que no este aprobado por la secretaria.)
* Reporte de Solicitud de compras imprimible (por ahora vacio)
* arvertencia al cancelar solicitud de que no puede des hacerse
* control de cantidades

PREGUNTAS:
* hay que limitar expediente en ubicación usuario? Idem para subisdios?
* cuando es obligatorio el tramite administrativo en solicitud de presupuesto? (o no es obligatorio?). Cuando es readonly? (idem para el tipo)
* hasta cuando puede modificar una solicitud de compra el area compras o la unidad de compras? Un estado distinto cuando ya está lista para aprobación por secretario? Un bloqueo
* algún control o filtro de solicitudes de compra? Cuales puede ver/modificar cada usuario?
* un menú para ver todos las solicitudes?
* por ahora el comprador (y solicitante) no puede ver las transacciones. Esta bien? o tenemos que darle permiso? Si no le damos permiso entonces no hay que mostrar botón
* Control de agregado de líneas a los requerimientos. Hasta cuando?
* tenemos que llevar precio unitario a la solicitud de compra? Y totales? Se puede editar? Tenemos que calcular el total? (si lo vez con nico habria que llevar el price_unit que agregamos a procurement.order)


Detalles:
- Llevar numero de requerimiento de abastecimiento:
  - a los picking
  - a las lineas de abastecimiento
- partner/usuario que pidio
- Limitar acceso de requirente a SOLO Pedidos de abastecimiento y que vea solo los suyos
- Dar posibilidad de edicion de Purchase Requisition a solicitante, ver de agregar opcion de menu para que no tenga que navegar hasta ahi


Si lo piden..
* hacer que se puedan sacar agregar proc.order desde una purchse requisition



.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.adhoc.com.ar/

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

* N/A

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

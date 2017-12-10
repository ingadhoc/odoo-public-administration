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
    * sec_administrativa / sec_administrativa (idem anterior)
    * sec_parlamentaria / sec_parlamentaria (idem anterior)
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
* Limitar acceso de requirente a SOLO Pedidos de abastecimiento y que vea solo los suyos (en realidad por ahora limitado para todos en el menú 'mis requerimientos')
* Reporte de Solicitud de compras imprimible (por ahora vacio)
NUEVAS
- Comprador no puede confirmar Orden de Compra: No se ha podido completar la operación por restricciones de seguridad. Contacte con su administrador del sistema. (era problema de multicompanía)
- Posibilidad de elegir tipos de transacciones a solicitante (se soluciona dando permiso de portal expedientes o secretaria usuario)
- Solicitante ni comprador pueden recibir productos: (Tipo de documento: stock.picking.type, Operación: read) (IDEM)
- Posibilidad de ver con usuario comprador todas los requerimientos, o que cada unidad de compra pueda ver los requerimientos que les hicieron a su unidad, no los puede ver ahora.  (quedamos que comprador no los ve pero los otros sí lo ven en su tarjeta del tablero de inventario)
- Con solicitante no puedo ver de manera sencilla el stock del producto: caso de uso, compre producto economato por 100 unidades, les di ingreso con usuario administrador, verifico stock en vista lista de productos con usuario solicitante y veo que el stock no cambio (estara en otra ubicacion?)
-generar usuario de pruebas secreataria administrativa (agregado usuarios para las dos secretarias)
* Compras tiene que poder unir las solicitudes de compra en una sola solicitud, con los numeros de solicitud concatenados. Ver bien que numeros unimos. (quedamos probar confcatenar)
* por ahora el comprador (y solicitante) no puede ver las transacciones. Esta bien? o tenemos que darle permiso? Si no le damos permiso entonces no hay que mostrar botón (se lo damos a compras)
* llevar precio a solicitudes de compra



Detalles para más adelante (y si los piden..)
----------------------------
- Ver tema traducciones, sobre todo para Licitaciones de Compra (Solicitudes) y Confirmar Licitacion (Aprobar Solicitud)
- Llevar numero de requerimiento de abastecimiento:
  - a los picking
  - a las lineas de abastecimiento
- partner/usuario que pidio
- Dar posibilidad de edicion de Purchase Requisition a solicitante, ver de agregar opcion de menu para que no tenga que navegar hasta ahi. Mmm no estoy seguro que sería..
* algún control o filtro de solicitudes de compra? Cuales puede ver/modificar cada usuario?
* cuando es obligatorio el tramite administrativo en solicitud de presupuesto? (o no es obligatorio?). Cuando es readonly? (idem para el tipo)
* hay que limitar expediente en ubicación usuario? Idem para subisdios?
* hacer que se puedan sacar agregar proc.order desde una purchse requisition
* hacemos el control de cantidades al confirmar pedidos de compras? Controlamos sumando por productos?
* hasta cuando puede modificar una solicitud de compra el area compras o la unidad de compras? Un estado distinto cuando ya está lista para aprobación por secretario? Un bloqueo
* Control de agregado de líneas a los requerimientos. Hasta cuando? (por ahí la dejamos para la 11 o vemos de bloquear con alguna lógica)


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

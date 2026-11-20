==========================
Sipreco Purchase Preaward
==========================

Preadjudicación de Solicitudes de Compra publicadas en la web: permite marcar
sobre las cotizaciones recibidas qué ítems se recomienda adjudicar a cada
oferente, registrar la desestimación y la justificación, e imprimir la planilla
de preadjudicación que acompaña el expediente.

Características
===============

- Marca "Preadjudicada" sobre la línea de la cotización
  (``purchase.order.line``), visible en el formulario de la orden cuando
  proviene de una Solicitud de Compra.
- Solapa "Preadjudicación" en la Solicitud de Compra, visible solo si la
  solicitud es publicable en web, con la desestimación, la justificación de la
  recomendación y el sello de quién imprimió la planilla y cuándo.
- Acción "Ofertas recibidas": abre en una sola lista las líneas de todas las
  cotizaciones de la solicitud, agrupadas por producto, para marcar las
  preadjudicadas comparando los oferentes entre sí.
- Acción "Poner en cero las no preadjudicadas": lleva a cero la cantidad de las
  líneas que quedaron fuera de la preadjudicación, sin tocar las cotizaciones
  ya confirmadas o canceladas.
- Reporte "Planilla de preadjudicación" en formato apaisado, con los datos del
  trámite, la comparativa de ofertas, el detalle de lo preadjudicado por
  proveedor, los totales por proveedor y el total general, la justificación y
  la firma.

Detalles Técnicos
=================

**Modelos heredados**

- ``purchase.order.line`` — se agrega ``preaward`` (Boolean), la marca de la
  línea elegida en la preadjudicación.
- ``purchase.requisition`` — se agregan ``preaward_dismissal`` (Text),
  ``preaward_justification`` (Text), ``preaward_user_id`` (M2o a ``res.users``,
  readonly) y ``preaward_date`` (Datetime, readonly). Métodos:
  ``print_preaward_report``, ``action_clear_unawarded_quantities``,
  ``action_open_quotation_lines``, ``get_preaward_rows``,
  ``get_preaward_purchases`` y ``get_preaward_detail``.

**Reportes**

- ``action_report_purchase_requisition_preaward`` — reporte QWeb PDF sobre
  ``purchase.requisition``, con un formato de papel A4 apaisado propio del
  módulo, porque el ancho de la comparativa depende de la cantidad de oferentes.

Arquitectura
============

La preadjudicación no agrega modelos: las ofertas ya son las cotizaciones de la
Solicitud de Compra, así que alcanza con una marca sobre la línea de la
cotización. La comparativa de la planilla reusa ``get_comparative_rows`` de
``sipreco_purchase``, el mismo cruce de ítems que usa el reporte de comparativa
de precios, para que los dos documentos muestren las ofertas igual.

Poner en cero las líneas que quedan afuera delega en ``action_clear_quantities``
de ``purchase_requisition``, que ya excluye las órdenes confirmadas o
canceladas. Las cantidades en cero conservan las ofertas desestimadas, que la
planilla necesita, y permiten volver a imprimirla.

Ni la confirmación ni la cancelación de las cotizaciones son automáticas: la
decisión y su ejecución quedan en manos de una persona.

Dependencias
============

- ``sipreco_purchase_web``

Autor
=====

ADHOC SA

Licencia
========

AGPL-3

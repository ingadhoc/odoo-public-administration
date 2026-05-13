==================================
Sipreco Purchase Web Publication
==================================

Publicación web de Solicitudes de Compra: expone en el sitio web público las
solicitudes de compra marcadas como publicables, con su documentación
descargable, estado, fechas y adjudicatarios.

Características
===============

- Marca de publicación web sobre la Solicitud de Compra (``purchase.requisition``):
  campo "Publicable en web" y control de "Publicado en web".
- Botones en el formulario de la Solicitud de Compra para **Publicar en web** y
  **Despublicar**, más un botón de estadística **Ver Sitio Web** que abre la
  ficha pública.
- Solapa "Datos para página web" (visible solo si la solicitud es publicable)
  con identificación pública, valor oficial (automático desde la SC o manual),
  fechas, estado público con barra de estado clicable y observaciones.
- Estado público independiente del estado interno: Para Apertura, En evaluación,
  Adjudicada, Finalizada, Desierta, Fracasada, Suspendida.
- Carga de archivos públicos por solicitud (pliegos, circulares, declaraciones
  juradas u otros), con orden por secuencia.
- Opción de exigir el ingreso de un email antes de permitir la descarga de un
  archivo ("muro de email"), registrando cada descarga en un log.
- Conteo de descargas por archivo y acceso al detalle de descargas registradas.
- Registro de adjudicatarios con su valor adjudicado y cálculo automático del
  valor total adjudicado.
- Sitio web público en ``/compras`` con listado filtrable por estado, ficha de
  detalle por solicitud y descarga de documentación.
- Entrada de menú "Compras y Contrataciones" en el sitio web.
- Actualización automática de la fecha de última actualización al modificar
  datos públicos de una solicitud ya publicada.

Detalles Técnicos
=================

**Modelos nuevos**

- ``purchase.web.attachment`` — Archivo público de Solicitud de Compra.
  Campos: ``sequence``, ``requisition_id`` (M2o a ``purchase.requisition``,
  ondelete cascade), ``name``, ``attachment_type`` (pliego/circular/ddjj/other),
  ``attachment`` (Binary) y ``attachment_fname``, ``require_email``,
  ``download_log_ids`` (O2m), ``download_count`` (computado). Métodos:
  ``_compute_download_count`` y ``action_view_download_logs``.
- ``purchase.web.award`` — Adjudicatario de Solicitud de Compra. Campos:
  ``requisition_id`` (M2o, ondelete cascade), ``partner_id`` (M2o a
  ``res.partner``), ``amount`` (Monetary), ``currency_id`` (related a
  ``requisition_id.currency_id``, store), ``notes``.
- ``purchase.web.download.log`` — Log de descargas de archivos públicos. Campos:
  ``attachment_line_id`` (M2o, ondelete cascade), ``requisition_id`` (related
  store), ``email``, ``download_date`` (default now, readonly). Orden por
  ``download_date desc``.

**Modelos heredados**

- ``purchase.requisition`` — se agregan campos de publicación web:
  ``web_publishable``, ``website_published``, ``web_number``, ``web_object``,
  ``web_amount``, ``web_amount_manual``, ``web_opening_datetime``,
  ``web_publication_date``, ``web_last_update``, ``web_state``,
  ``web_observations`` (Html), ``web_award_ids`` (O2m), ``web_total_awarded``
  (Monetary computado, store), ``web_attachment_ids`` (O2m).
  Lógica: ``_compute_web_total_awarded`` (depende de ``web_award_ids.amount``),
  onchange ``_onchange_web_amount_manual`` y ``_onchange_web_publishable``,
  override de ``write`` (sincroniza ``website_published`` y ``web_last_update``),
  y acciones ``action_web_publish``, ``action_web_unpublish``,
  ``action_view_website``.

**Vistas incluidas**

- Formulario de ``purchase.requisition`` heredado: botones de publicar/
  despublicar, botón de estadística "Ver Sitio Web", campo "Publicable en web"
  y solapa "Datos para página web" con sub-páginas de Archivos públicos y
  Adjudicatarios.
- Lista de ``purchase.requisition`` heredada con columnas de publicación.
- Búsqueda de ``purchase.requisition`` heredada con filtros "Publicables en web"
  y "Publicadas en web".
- Formulario de ``purchase.web.attachment`` con botón de descargas.
- Formulario de ``purchase.web.award``.
- Lista de solo lectura de ``purchase.web.download.log`` y acción de ventana
  ``action_purchase_web_download_log``.

**Plantillas de sitio web (QWeb)**

- ``purchase_list_template`` — listado público con filtros por estado.
- ``purchase_detail_template`` — ficha de detalle de una solicitud.
- ``purchase_email_gate_template`` — formulario de email previo a la descarga.

**Controlador** (``controllers/main.py``, rutas públicas ``website=True``)

- ``GET /compras`` — listado de solicitudes publicadas, filtrable por ``state``.
- ``GET /compras/<id>`` — detalle de una solicitud publicada.
- ``GET /compras/<id>/descargar/<attachment_line_id>`` — descarga de archivo;
  si el archivo exige email, muestra el muro de email.
- ``POST /compras/<id>/descargar/<attachment_line_id>/email`` — recepción del
  email (con CSRF), validación básica y redirección a la descarga.

**Seguridad**

- ``ir.model.access.csv``: acceso completo para ``purchase.group_purchase_user``
  sobre los tres modelos nuevos; lectura para ``base.group_public`` sobre
  ``purchase.web.attachment`` y ``purchase.web.award``.
- ``ir.rule`` ``purchase_requisition_public_rule``: el grupo público solo puede
  leer solicitudes con ``website_published`` y ``web_publishable`` en ``True``.

**Menú**

- ``website.menu`` "Compras y Contrataciones" apuntando a ``/compras``.

Uso
===

1. En una Solicitud de Compra (``purchase.requisition``), marcar el campo
   **Publicable en web**.
2. Completar la solapa **Datos para página web**: número, objeto, valor oficial
   (automático desde la SC o activando "Monto manual"), fecha y hora de apertura,
   estado público y observaciones.
3. En la sub-página **Archivos públicos**, agregar la documentación (pliegos,
   circulares, etc.), indicando el tipo y, si corresponde, marcando "Solicitar
   email para descarga".
4. Cuando la solicitud esté Finalizada/Adjudicada, cargar los **Adjudicatarios**
   con su valor; el total adjudicado se calcula automáticamente.
5. Presionar **Publicar en web**. Se registra la fecha de publicación y la
   solicitud queda visible en ``/compras``. Usar **Despublicar** para retirarla.
6. Usar el botón **Ver Sitio Web** para abrir la ficha pública en una pestaña
   nueva.
7. En el sitio público, los visitantes navegan el listado en
   "Compras y Contrataciones", filtran por estado, abren el detalle y descargan
   los archivos. Si un archivo exige email, se solicita antes de la descarga y
   se registra en el log de descargas.

Arquitectura
============

El módulo extiende ``purchase.requisition`` con un conjunto de campos de
publicación y tres modelos satélite relacionados por Many2one con borrado en
cascada: archivos públicos, adjudicatarios y log de descargas. La capa de
presentación pública se resuelve con un controlador HTTP (``website=True``,
``auth="public"``, accesos vía ``sudo()``) que renderiza plantillas QWeb,
protegida por una ``ir.rule`` que limita la lectura pública a las solicitudes
efectivamente publicadas. Las descargas con muro de email registran cada acceso
en ``purchase.web.download.log``, alimentando el contador de descargas por
archivo. El override de ``write`` mantiene la coherencia entre publicación y
fecha de última actualización.

Dependencias
============

- ``sipreco_purchase``
- ``website``
- ``mail``

Autor
=====

ADHOC SA

Licencia
========

AGPL-3

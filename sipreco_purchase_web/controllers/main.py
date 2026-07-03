##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import json
import logging
import mimetypes
from urllib.parse import urlencode

from odoo.http import request

from odoo import http

_logger = logging.getLogger(__name__)

_WEB_STATES = {
    "open": "Para Apertura",
    "evaluation": "En evaluación",
    "awarded": "Adjudicada",
    "finished": "Finalizada",
    "void": "Desierta",
    "failed": "Fracasada",
    "suspended": "Suspendida",
}

# Tipos de archivo con etiqueta para plantilla
_ATTACHMENT_TYPE_LABELS = {
    "pliego": "Pliego",
    "circular": "Circular aclaratoria/modificatoria",
    "ddjj": "Declaración jurada",
    "other": "Otro",
}


def _set_embed_headers(response):
    # X-Frame-Options: ALLOWALL no existe en el estándar; basta con CSP
    response.headers.pop("X-Frame-Options", None)
    response.headers["Content-Security-Policy"] = "frame-ancestors *"


_WIDGET_JS = r"""
(function () {
    var script = document.currentScript;
    var baseUrl = new URL(script.src).origin;
    var targetId = (script.dataset && script.dataset.target) || 'cmr-compras';
    var container = document.getElementById(targetId);
    if (!container) return;

    var STATES = {
        open:       { label: 'Para Apertura',  bg: '#0d6efd', color: '#fff' },
        evaluation: { label: 'En evaluación', bg: '#ffc107', color: '#000' },
        awarded:    { label: 'Adjudicada',     bg: '#198754', color: '#fff' },
        finished:   { label: 'Finalizada',     bg: '#6c757d', color: '#fff' },
        void:       { label: 'Desierta',       bg: '#dc3545', color: '#fff' },
        failed:     { label: 'Fracasada',      bg: '#dc3545', color: '#fff' },
        suspended:  { label: 'Suspendida',     bg: '#fd7e14', color: '#fff' },
    };

    var allPurchases = [];
    var activeState  = null;

    function esc(str) {
        return String(str || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function badgeHtml(state) {
        var s = STATES[state];
        if (!s) return '';
        return '<span style="display:inline-block;padding:2px 8px;border-radius:4px;'
            + 'font-size:12px;font-weight:600;background:' + s.bg + ';color:' + s.color + '">'
            + esc(s.label) + '</span>';
    }

    function filterBtnHtml(state, label) {
        var active = state === activeState;
        return '<button data-cmr-state="' + (state || '') + '" style="'
            + 'cursor:pointer;padding:4px 12px;border-radius:4px;font-size:13px;margin:2px;'
            + 'border:1px solid ' + (active ? '#333' : '#ccc') + ';'
            + 'background:' + (active ? '#333' : '#fff') + ';'
            + 'color:' + (active ? '#fff' : '#555') + '">'
            + esc(label) + '</button>';
    }

    function renderList(purchases) {
        var filtered = activeState
            ? purchases.filter(function (p) { return p.state === activeState; })
            : purchases;

        var html = '<div style="font-family:inherit">';

        html += '<div style="margin-bottom:12px">';
        html += filterBtnHtml(null, 'Todos');
        Object.keys(STATES).forEach(function (s) {
            html += filterBtnHtml(s, STATES[s].label);
        });
        html += '</div>';

        if (!filtered.length) {
            html += '<p style="color:#888;margin:16px 0">No hay compras publicadas actualmente.</p>';
        } else {
            filtered.forEach(function (p) {
                html += '<div style="border:1px solid #dee2e6;border-radius:6px;padding:14px 16px;'
                    + 'margin-bottom:10px;background:#fff">';
                html += '<div style="display:flex;justify-content:space-between;'
                    + 'align-items:center;flex-wrap:wrap;gap:8px">';

                html += '<div style="flex:1;min-width:180px">';
                if (p.number) {
                    html += '<span style="color:#999;font-size:13px;margin-right:6px">'
                        + esc(p.number) + '</span>';
                }
                html += '<strong style="font-size:15px">' + esc(p.object) + '</strong>';
                if (p.type) {
                    html += '<div style="font-size:13px;color:#666;margin-top:3px">'
                        + 'Tipo: ' + esc(p.type) + '</div>';
                }
                if (p.opening_date) {
                    html += '<div style="font-size:13px;color:#666">'
                        + 'Apertura: ' + esc(p.opening_date) + '</div>';
                }
                html += '</div>';

                html += '<div style="display:flex;align-items:center;gap:8px;flex-shrink:0">';
                html += badgeHtml(p.state);
                html += '<a href="' + baseUrl + '/compras/' + p.id + '" target="_blank" '
                    + 'rel="noopener" style="padding:5px 12px;border:1px solid #0d6efd;'
                    + 'border-radius:4px;color:#0d6efd;text-decoration:none;'
                    + 'font-size:13px;white-space:nowrap">Ver detalle</a>';
                html += '</div>';

                html += '</div></div>';
            });
        }

        html += '</div>';
        return html;
    }

    container.addEventListener('click', function (e) {
        var btn = e.target.closest('[data-cmr-state]');
        if (!btn) return;
        activeState = btn.dataset.cmrState || null;
        container.innerHTML = renderList(allPurchases);
    });

    container.innerHTML = '<p style="color:#aaa;font-size:13px;padding:8px 0">Cargando compras…</p>';

    fetch(baseUrl + '/compras/json')
        .then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json();
        })
        .then(function (data) {
            allPurchases = data;
            container.innerHTML = renderList(data);
        })
        .catch(function () {
            container.innerHTML = '<p style="color:#c00;padding:8px 0">'
                + 'No se pudo cargar la información. Intentá más tarde.</p>';
        });
})();
"""


class PurchaseWebController(http.Controller):
    @http.route("/compras", type="http", auth="public", website=True)
    def purchase_list(self, state=None, embed=False, **kwargs):
        domain = [
            ("website_published", "=", True),
            ("web_publishable", "=", True),
        ]
        if state and state in _WEB_STATES:
            domain.append(("web_state", "=", state))
        Requisition = request.env["purchase.requisition"].sudo()
        purchases = Requisition.search(
            domain, order="web_publication_date desc, id desc"
        )
        template = (
            "sipreco_purchase_web.purchase_list_embed_template"
            if embed
            else "sipreco_purchase_web.purchase_list_template"
        )
        response = request.render(
            template,
            {
                "purchases": purchases,
                "web_states": _WEB_STATES,
                "current_state": state,
                "page_name": "purchase_list",
                "embed": bool(embed),
            },
        )
        if embed:
            _set_embed_headers(response)
        return response

    @http.route("/compras/<int:purchase_id>", type="http", auth="public", website=True)
    def purchase_detail(self, purchase_id, embed=False, **kwargs):
        Requisition = request.env["purchase.requisition"].sudo()
        purchase = Requisition.search(
            [
                ("id", "=", purchase_id),
                ("website_published", "=", True),
                ("web_publishable", "=", True),
            ],
            limit=1,
        )

        if not purchase:
            return request.not_found()

        template = (
            "sipreco_purchase_web.purchase_detail_embed_template"
            if embed
            else "sipreco_purchase_web.purchase_detail_template"
        )
        response = request.render(
            template,
            {
                "purchase": purchase,
                "web_states": _WEB_STATES,
                "attachment_type_labels": _ATTACHMENT_TYPE_LABELS,
                "page_name": "purchase_detail",
                "embed": bool(embed),
            },
        )
        if embed:
            _set_embed_headers(response)
        return response

    @http.route(
        "/compras/<int:purchase_id>/descargar/<int:attachment_line_id>",
        type="http",
        auth="public",
        website=True,
    )
    def purchase_attachment_download(
        self, purchase_id, attachment_line_id, embed=False, **kwargs
    ):
        attachment_line = (
            request.env["purchase.web.attachment"]
            .sudo()
            .search(
                [
                    ("id", "=", attachment_line_id),
                    ("requisition_id", "=", purchase_id),
                    ("requisition_id.website_published", "=", True),
                    ("requisition_id.web_publishable", "=", True),
                ],
                limit=1,
            )
        )
        if not attachment_line:
            return request.not_found()
        purchase = attachment_line.requisition_id

        if attachment_line.require_email:
            email = kwargs.get("email", "").strip()
            if not email:
                template = (
                    "sipreco_purchase_web.purchase_email_gate_embed_template"
                    if embed
                    else "sipreco_purchase_web.purchase_email_gate_template"
                )
                response = request.render(
                    template,
                    {
                        "purchase": purchase,
                        "attachment_line": attachment_line,
                        "page_name": "purchase_email_gate",
                        "embed": bool(embed),
                    },
                )
                if embed:
                    _set_embed_headers(response)
                return response
            _logger.info(
                'Descarga de archivo "%s" (id=%s) por email: %s',
                attachment_line.name,
                attachment_line_id,
                email,
            )
            request.env["purchase.web.download.log"].sudo().create(
                {
                    "attachment_line_id": attachment_line.id,
                    "email": email,
                }
            )

        if not attachment_line.attachment:
            return request.not_found()

        fname = attachment_line.attachment_fname or "archivo"
        mimetype, _ = mimetypes.guess_type(fname)
        stream = http.Stream.from_binary_field(attachment_line, 'attachment')
        stream.download_name = fname
        stream.as_attachment = True
        if mimetype:
            stream.mimetype = mimetype
        return stream.get_response()

    @http.route(
        "/compras/<int:purchase_id>/descargar/<int:attachment_line_id>/email",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def purchase_attachment_email_submit(
        self, purchase_id, attachment_line_id, email="", embed=False, **kwargs
    ):
        # Validación básica del email recibido por POST
        email = email.strip()
        base_url = "/compras/%d/descargar/%d" % (purchase_id, attachment_line_id)
        if not email or "@" not in email:
            params = {"embed": 1} if embed else {}
            qs = "?" + urlencode(params) if params else ""
            return request.redirect(base_url + qs)
        _logger.info(
            "Email registrado para descarga de archivo (requisition=%d, attachment=%d): %s",
            purchase_id,
            attachment_line_id,
            email,
        )
        params = {"email": email}
        if embed:
            params["embed"] = 1
        return request.redirect(base_url + "?" + urlencode(params))

    @http.route("/compras/json", type="http", auth="public", methods=["GET"], csrf=False)
    def purchase_list_json(self, state=None, **kwargs):
        domain = [
            ("website_published", "=", True),
            ("web_publishable", "=", True),
        ]
        if state and state in _WEB_STATES:
            domain.append(("web_state", "=", state))
        purchases = (
            request.env["purchase.requisition"]
            .sudo()
            .search(domain, order="web_publication_date desc, id desc")
        )
        data = [
            {
                "id": p.id,
                "number": p.web_number or "",
                "object": p.web_object or p.name or "",
                "type": p.transaction_type_id.name if p.transaction_type_id else "",
                "state": p.web_state or "",
                "state_label": _WEB_STATES.get(p.web_state, p.web_state or ""),
                "opening_date": (
                    p.web_opening_datetime.strftime("%d/%m/%Y %H:%M")
                    if p.web_opening_datetime
                    else ""
                ),
                "publication_date": (
                    p.web_publication_date.strftime("%d/%m/%Y")
                    if p.web_publication_date
                    else ""
                ),
            }
            for p in purchases
        ]
        return request.make_response(
            json.dumps(data, ensure_ascii=False),
            headers=[
                ("Content-Type", "application/json; charset=utf-8"),
                ("Access-Control-Allow-Origin", "*"),
                ("Access-Control-Allow-Methods", "GET, OPTIONS"),
            ],
        )

    @http.route("/compras/widget.js", type="http", auth="public", methods=["GET"])
    def purchase_widget_js(self, **kwargs):
        return request.make_response(
            _WIDGET_JS,
            headers=[("Content-Type", "application/javascript; charset=utf-8")],
        )

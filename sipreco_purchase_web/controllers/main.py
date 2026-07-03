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


_WIDGET_JS = r"""
(function () {
    var script = document.currentScript;
    if (!script || !script.src) {
        var tags = document.querySelectorAll('script[src*="/compras/widget.js"]');
        script = tags[tags.length - 1] || null;
    }
    var baseUrl = (script && script.src)
        ? new URL(script.src).origin
        : window.location.origin;
    var targetId = (script && script.dataset && script.dataset.target) || 'cmr-compras';
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

    function formatAmount(n, symbol) {
        var s = Number(n).toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        return esc(symbol) + ' ' + s;
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
                html += '<button data-cmr-id="' + p.id + '" style="cursor:pointer;padding:5px 12px;'
                    + 'border:1px solid #0d6efd;border-radius:4px;background:#fff;'
                    + 'color:#0d6efd;font-size:13px;white-space:nowrap">Ver detalle</button>';
                html += '</div>';

                html += '</div></div>';
            });
        }

        html += '</div>';
        return html;
    }

    function renderDetail(p) {
        var html = '<div style="font-family:inherit">';

        html += '<button data-cmr-back="" style="cursor:pointer;padding:4px 12px;border-radius:4px;'
            + 'font-size:13px;margin-bottom:16px;border:1px solid #ccc;background:#fff;color:#555">'
            + '← Volver al listado</button>';

        html += '<h2 style="font-size:20px;margin:0 0 6px">';
        if (p.number) {
            html += '<span style="color:#999;font-size:15px;margin-right:8px">' + esc(p.number) + '</span>';
        }
        html += esc(p.object) + '</h2>';
        html += badgeHtml(p.state);

        html += '<hr style="margin:16px 0"/>';

        html += '<dl style="display:grid;grid-template-columns:auto 1fr;gap:4px 16px;font-size:14px">';
        if (p.type) {
            html += '<dt style="color:#666;white-space:nowrap">Tipo de compra</dt>'
                + '<dd style="margin:0">' + esc(p.type) + '</dd>';
        }
        if (p.amount && p.currency_symbol) {
            html += '<dt style="color:#666;white-space:nowrap">Valor oficial</dt>'
                + '<dd style="margin:0">' + formatAmount(p.amount, p.currency_symbol) + '</dd>';
        }
        if (p.opening_date) {
            html += '<dt style="color:#666;white-space:nowrap">Apertura</dt>'
                + '<dd style="margin:0">' + esc(p.opening_date) + '</dd>';
        }
        if (p.publication_date) {
            html += '<dt style="color:#666;white-space:nowrap">Publicación</dt>'
                + '<dd style="margin:0">' + esc(p.publication_date) + '</dd>';
        }
        if (p.last_update) {
            html += '<dt style="color:#666;white-space:nowrap">Última actualización</dt>'
                + '<dd style="margin:0">' + esc(p.last_update) + '</dd>';
        }
        html += '</dl>';

        if (p.observations_html) {
            html += '<h4 style="font-size:15px;margin:20px 0 8px">Observaciones</h4>'
                + '<div style="font-size:14px">' + p.observations_html + '</div>';
        }

        if (p.awards && p.awards.length) {
            html += '<h4 style="font-size:15px;margin:20px 0 8px">Adjudicación</h4>';
            html += '<table style="width:100%;border-collapse:collapse;font-size:13px">'
                + '<thead><tr style="background:#f8f9fa">'
                + '<th style="padding:6px 10px;text-align:left;border:1px solid #dee2e6">Adjudicatario</th>'
                + '<th style="padding:6px 10px;text-align:left;border:1px solid #dee2e6">Valor</th>'
                + '<th style="padding:6px 10px;text-align:left;border:1px solid #dee2e6">Detalle</th>'
                + '</tr></thead><tbody>';
            p.awards.forEach(function (a) {
                html += '<tr>'
                    + '<td style="padding:6px 10px;border:1px solid #dee2e6">' + esc(a.partner) + '</td>'
                    + '<td style="padding:6px 10px;border:1px solid #dee2e6">' + formatAmount(a.amount, a.currency_symbol) + '</td>'
                    + '<td style="padding:6px 10px;border:1px solid #dee2e6">' + esc(a.notes) + '</td>'
                    + '</tr>';
            });
            html += '</tbody></table>';
        }

        if (p.attachments && p.attachments.length) {
            html += '<h4 style="font-size:15px;margin:20px 0 8px">Documentación</h4>'
                + '<ul style="list-style:none;padding:0;margin:0">';
            p.attachments.forEach(function (att) {
                html += '<li style="padding:8px 0;border-bottom:1px solid #f0f0f0">'
                    + '<a href="' + baseUrl + '/compras/' + p.id + '/descargar/' + att.id + '" '
                    + 'target="_blank" rel="noopener" '
                    + 'style="color:#0d6efd;text-decoration:none;font-size:14px">'
                    + '↓ ' + esc(att.name);
                if (att.type_label) {
                    html += '<span style="color:#888;font-size:12px;margin-left:6px">'
                        + esc(att.type_label) + '</span>';
                }
                html += '</a></li>';
            });
            html += '</ul>';
        }

        html += '</div>';
        return html;
    }

    container.addEventListener('click', function (e) {
        if (e.target.closest('[data-cmr-back]')) {
            container.innerHTML = renderList(allPurchases);
            return;
        }
        var stateBtn = e.target.closest('[data-cmr-state]');
        if (stateBtn) {
            activeState = stateBtn.dataset.cmrState || null;
            container.innerHTML = renderList(allPurchases);
            return;
        }
        var detailBtn = e.target.closest('[data-cmr-id]');
        if (detailBtn) {
            var id = detailBtn.dataset.cmrId;
            container.innerHTML = '<p style="color:#aaa;font-size:13px;padding:8px 0">Cargando…</p>';
            fetch(baseUrl + '/compras/' + id + '/json')
                .then(function (r) {
                    if (!r.ok) throw new Error('HTTP ' + r.status);
                    return r.json();
                })
                .then(function (data) {
                    container.innerHTML = renderDetail(data);
                })
                .catch(function () {
                    container.innerHTML = '<p style="color:#c00;padding:8px 0">'
                        + 'No se pudo cargar el detalle. Intentá más tarde.</p>';
                });
        }
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
    def purchase_list(self, state=None, **kwargs):
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
        return request.render(
            "sipreco_purchase_web.purchase_list_template",
            {
                "purchases": purchases,
                "web_states": _WEB_STATES,
                "current_state": state,
                "page_name": "purchase_list",
            },
        )

    @http.route("/compras/<int:purchase_id>", type="http", auth="public", website=True)
    def purchase_detail(self, purchase_id, **kwargs):
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

        return request.render(
            "sipreco_purchase_web.purchase_detail_template",
            {
                "purchase": purchase,
                "web_states": _WEB_STATES,
                "attachment_type_labels": _ATTACHMENT_TYPE_LABELS,
                "page_name": "purchase_detail",
            },
        )

    @http.route(
        "/compras/<int:purchase_id>/descargar/<int:attachment_line_id>",
        type="http",
        auth="public",
        website=True,
    )
    def purchase_attachment_download(
        self, purchase_id, attachment_line_id, **kwargs
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
                return request.render(
                    "sipreco_purchase_web.purchase_email_gate_template",
                    {
                        "purchase": purchase,
                        "attachment_line": attachment_line,
                        "page_name": "purchase_email_gate",
                    },
                )
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
        self, purchase_id, attachment_line_id, email="", **kwargs
    ):
        # Validación básica del email recibido por POST
        email = email.strip()
        base_url = "/compras/%d/descargar/%d" % (purchase_id, attachment_line_id)
        if not email or "@" not in email:
            return request.redirect(base_url)
        _logger.info(
            "Email registrado para descarga de archivo (requisition=%d, attachment=%d): %s",
            purchase_id,
            attachment_line_id,
            email,
        )
        return request.redirect(base_url + "?" + urlencode({"email": email}))

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

    @http.route("/compras/<int:purchase_id>/json", type="http", auth="public", methods=["GET"], csrf=False)
    def purchase_detail_json(self, purchase_id, **kwargs):
        purchase = (
            request.env["purchase.requisition"]
            .sudo()
            .search(
                [
                    ("id", "=", purchase_id),
                    ("website_published", "=", True),
                    ("web_publishable", "=", True),
                ],
                limit=1,
            )
        )
        if not purchase:
            return request.make_response(
                json.dumps({"error": "not_found"}, ensure_ascii=False),
                headers=[
                    ("Content-Type", "application/json; charset=utf-8"),
                    ("Access-Control-Allow-Origin", "*"),
                ],
            )
        data = {
            "id": purchase.id,
            "number": purchase.web_number or "",
            "object": purchase.web_object or purchase.name or "",
            "type": purchase.transaction_type_id.name if purchase.transaction_type_id else "",
            "state": purchase.web_state or "",
            "state_label": _WEB_STATES.get(purchase.web_state, purchase.web_state or ""),
            "opening_date": (
                purchase.web_opening_datetime.strftime("%d/%m/%Y %H:%M")
                if purchase.web_opening_datetime
                else ""
            ),
            "publication_date": (
                purchase.web_publication_date.strftime("%d/%m/%Y")
                if purchase.web_publication_date
                else ""
            ),
            "last_update": (
                purchase.web_last_update.strftime("%d/%m/%Y")
                if purchase.web_last_update
                else ""
            ),
            "currency_symbol": purchase.currency_id.symbol if purchase.currency_id else "",
            "amount": (
                purchase.web_amount if purchase.web_amount_manual else purchase.amount_total
            ),
            "observations_html": purchase.web_observations or "",
            "awards": [
                {
                    "partner": award.partner_id.name or "",
                    "currency_symbol": award.currency_id.symbol if award.currency_id else "",
                    "amount": award.amount,
                    "notes": award.notes or "",
                }
                for award in purchase.web_award_ids
            ],
            "attachments": [
                {
                    "id": att.id,
                    "name": att.name or "",
                    "type_label": _ATTACHMENT_TYPE_LABELS.get(att.attachment_type, ""),
                }
                for att in purchase.web_attachment_ids
            ],
        }
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

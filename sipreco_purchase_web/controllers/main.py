##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
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
        template = "sipreco_purchase_web.purchase_list_template"
        response = request.render(
            template,
            {
                "purchases": purchases,
                "web_states": _WEB_STATES,
                "current_state": state,
                "page_name": "purchase_list",
            },
        )
        return response

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

        template = "sipreco_purchase_web.purchase_detail_template"
        response = request.render(
            template,
            {
                "purchase": purchase,
                "web_states": _WEB_STATES,
                "attachment_type_labels": _ATTACHMENT_TYPE_LABELS,
                "page_name": "purchase_detail",
            },
        )
        return response

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
                template = "sipreco_purchase_web.purchase_email_gate_template"
                response = request.render(
                    template,
                    {
                        "purchase": purchase,
                        "attachment_line": attachment_line,
                        "page_name": "purchase_email_gate",
                    },
                )
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
        self, purchase_id, attachment_line_id, email="", **kwargs
    ):
        # Validación básica del email recibido por POST
        email = email.strip()
        base_url = "/compras/%d/descargar/%d" % (purchase_id, attachment_line_id)
        if not email or "@" not in email:
            qs = urlencode({"email": email, "error": "invalid_email"})
            return request.redirect(base_url + "?" + qs)
        return request.redirect(base_url + "?" + urlencode({"email": email}))

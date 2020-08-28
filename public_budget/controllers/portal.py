from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class CustomerPortal(CustomerPortal):

    @http.route()
    def home(self, **kw):
        # Anulamos portal para este caso que simpre redirija a backend
        return request.redirect('/web')

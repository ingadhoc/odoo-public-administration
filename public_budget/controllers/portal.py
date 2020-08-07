from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.web import Home as PortalHome
from odoo.addons.web.controllers.main import Home
from odoo.http import request


class CustomerPortal(CustomerPortal):

    @http.route()
    def home(self, **kw):
        # Anulamos portal para este caso que simpre redirija a backend
        return request.redirect('/web')


class PortalHome(PortalHome):

    @http.route()
    def web_client(self, s_action=None, **kw):
        if request.session.uid and request.env['res.users'].sudo().browse(
                request.session.uid).has_group('base.group_portal'):
            return Home.web_client(self, s_action=s_action, **kw)
        return super(PortalHome, self).web_client(s_action, **kw)

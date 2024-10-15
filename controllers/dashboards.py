import logging
import base64

from odoo import fields
from odoo.http import request, route, content_disposition
from odoo import http, tools, _

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.models.website import slugify
from werkzeug.utils import redirect
from  datetime import timedelta

class DashBoardsCustom(http.Controller):

    @http.route('/custom_dashboard/test', type='json', auth='user')
    def dashboard_test_call(self, **kw):
        print(kw)
        partners = request.env['res.partner'].search([])
        return {'partners': partners.mapped('name'), 'username': request.env.user.name}

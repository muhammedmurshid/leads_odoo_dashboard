import logging
import base64

from odoo import fields
from odoo.http import request, route, content_disposition
from odoo import http, tools, _

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.models.website import slugify
from werkzeug.utils import redirect
from datetime import timedelta,datetime
from . import helpers as helper_tools
class DashBoardsCustom(http.Controller):

    @http.route('/custom_dashboard/get_dashboard_data', type='json', auth='user')
    def dashboard_test_call(self, **kw):
        print(kw)
        partners = request.env['res.partner'].search([])
        dashboardStats = {}
        dashboardStats.update(self.get_sales_data())
        return {'partners': partners.mapped('name'), 'username': request.env.user.name, 'dashboardStats': dashboardStats}

    def get_sales_data(self):
        return {
            'sales_today': self.get_sales_revenue(period='today'),
            'sales_this_week':self.get_sales_revenue(period='week'),
            'sales_this_month':self.get_sales_revenue(period='month'),
            'sales_this_quarter':self.get_sales_revenue(period='quarter'),
            'sales_this_year':self.get_sales_revenue(period='year'),
        }
    
    def get_date_range(self, period="today"):
        today = fields.Date.today()
        start_date = end_date = None

        if period == 'today':
            start_date = datetime.combine(today, datetime.min.time())
            end_date = datetime.combine(today, datetime.max.time())
        elif period == 'week':
            start_date = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
            end_date = datetime.combine(today + timedelta(days=6 - today.weekday()), datetime.max.time())
        elif period == 'month':
            start_date = datetime.combine(today.replace(day=1), datetime.min.time())
            last_day = (today.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            end_date = datetime.combine(last_day, datetime.max.time())
        elif period == 'quarter':
            quarter = (today.month - 1) // 3 + 1
            start_month = 3 * (quarter - 1) + 1
            start_date = datetime.combine(today.replace(month=start_month, day=1), datetime.min.time())
            end_month = start_month + 2
            last_day = (today.replace(month=end_month, day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            end_date = datetime.combine(last_day, datetime.max.time())
        elif period == 'year':
            start_date = datetime.combine(today.replace(month=1, day=1), datetime.min.time())
            end_date = datetime.combine(today.replace(month=12, day=31), datetime.max.time())
        return start_date, end_date
    
    @http.route('/custom_dashboard/sales_revenue_domain', type='json', auth='user')
    def get_sales_revenue_domain(self, **kw):
        period = kw.get('period', 'today')
        start_date, end_date = self.get_date_range(period)
        domain = [('state', 'in', ['sale', 'done']), ('date_order', '>=', start_date), ('date_order', '<=', end_date),]
        return domain

    def get_sales_revenue(self, period='today'):
        domain = self.get_sales_revenue_domain(period=period)
        orders = request.env['sale.order'].search(domain)
        # Sum up the total amounts
        total_revenue = int(sum(order.amount_total for order in orders))
        return helper_tools.format_to_indian_currency(total_revenue)
        # return round(total_revenue,3)

import logging
import base64
from datetime import date, timedelta
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
    def dashboard_test_call(self, from_date=None, to_date=None, **kw):
        # Convert dates from strings if provided
        # print("Received Dates:", from_date, to_date)
        if from_date and to_date:
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
            to_date = datetime.strptime(to_date, "%Y-%m-%d")
            # print('dates', from_date, to_date)
        print(kw)
        partners = request.env['res.partner'].search([])
        dashboardStats = {}
        dashboardStats.update(self.get_sales_data(from_date, to_date))
        return {'partners': partners.mapped('name'), 'username': request.env.user.name, 'dashboardStats': dashboardStats}

    def get_sales_data(self, from_date=None, to_date=None):
        if from_date:
            from_date = fields.Date.from_string(from_date)
            print(from_date, 'from_date')
        if to_date:
            to_date = fields.Date.from_string(to_date)
            print(to_date, 'to')
        employee_sales_data = self.get_employee_sales_data(from_date,to_date)
        # product_sales_data = self.get_product_sales_data(from_date,to_date)
        zero_sales_employees = self.get_employees_with_zero_sales(from_date,to_date)
        employee_source_data, all_sources = self.get_employee_lead_source_data(from_date, to_date)
        employee_quality_data, quality_labels, quality_keys = self.get_employee_lead_quality_data(from_date, to_date)
        return {
            'sales_today': self.get_sales_revenue(period='today' ),
            'sales_this_week': self.get_sales_revenue(period='week'),
            'sales_this_month': self.get_sales_revenue(period='month'),
            'sales_this_quarter': self.get_sales_revenue(period='quarter'),
            'sales_this_year': self.get_sales_revenue(period='year'),
            'employee_source_data': employee_source_data,
            'all_sources': all_sources,
            'employee_sales_data': employee_sales_data,
            'employee_quality_data': employee_quality_data,
            'lead_quality_labels': quality_labels,
            'lead_quality_keys': quality_keys,

        }

    def get_date_range(self, period="today"):
        today = date.today()

        if period == 'today':
            start_date = end_date = today

        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())  # Monday
            end_date = start_date + timedelta(days=6)  # Sunday

        elif period == 'month':
            start_date = today.replace(day=1)
            next_month = start_date.replace(day=28) + timedelta(days=4)  # ensures next month
            end_date = next_month.replace(day=1) - timedelta(days=1)

        elif period == 'quarter':
            quarter = (today.month - 1) // 3 + 1
            start_month = 3 * (quarter - 1) + 1
            start_date = date(today.year, start_month, 1)
            if start_month + 2 > 12:
                end_date = date(today.year, 12, 31)
            else:
                next_month = date(today.year, start_month + 3, 1)
                end_date = next_month - timedelta(days=1)

        elif period == 'year':
            start_date = date(today.year, 1, 1)
            end_date = date(today.year, 12, 31)

        else:
            start_date = end_date = today  # default fallback

        return start_date, end_date

    @http.route('/custom_dashboard/sales_revenue_domain', type='json', auth='user')
    def get_sales_revenue_domain(self, **kw):
        period = kw.get('period', 'today')
        start_date, end_date = self.get_date_range(period)

        domain = [
            ('lead_quality', '=', 'admission'),
            ('admission_date', '>=', start_date),
            ('admission_date', '<=', end_date),
        ]
        return domain

    def get_employees_with_zero_sales(self, from_date=None, to_date=None):
        users = request.env['res.users'].search([('employee_id.department_id.name', '=', 'Sales')])  # Get all users
        zero_sales_employees = []

        # Convert string dates to datetime objects if provided
        if from_date:
            from_date = fields.Date.from_string(from_date)
        if to_date:
            to_date = fields.Date.from_string(to_date)

        for user in users:
            # Build domain for sales orders
            domain = [
                ('user_id', '=', user.id),
                ('state', 'in', ['sale', 'done'])
            ]
            if from_date and to_date:
                domain += [('date_order', '>=', from_date), ('date_order', '<=', to_date)]

            # Check if the user has any sales orders in the specified date range
            sales_orders = request.env['sale.order'].search(domain)
            if not sales_orders:
                print('No sale orders found for user:', user.name)  # Debugging line
                zero_sales_employees.append(
                    {'id': user.id, 'name': user.name})  # Add user to the list if no sales orders found

        return zero_sales_employees

    def get_employee_lead_source_data(self, from_date=None, to_date=None):
        users = request.env['res.users'].search([
            ('employee_id.department_id.name', '=', 'Sales')
        ])
        sources = request.env['leads.sources'].search([])
        all_sources = [s.name for s in sources]

        employee_sales_data = []
        total_row = {source: 0 for source in all_sources}
        total_row['employee_name'] = 'Total'
        total_row['total_count'] = 0

        if from_date:
            from_date = fields.Date.from_string(from_date)
        if to_date:
            to_date = fields.Date.from_string(to_date)

        for user in users:
            source_map = {source_name: 0 for source_name in all_sources}
            total_count = 0

            for source in sources:
                domain = [
                    ('lead_owner', '=', user.employee_id.id),
                    ('state', '=', 'qualified'),
                    ('leads_source', '=', source.id),
                ]
                if from_date and to_date:
                    domain += [
                        ('admission_date', '>=', from_date),
                        ('admission_date', '<=', to_date)
                    ]

                leads = request.env['leads.logic'].search(domain)
                count = len(leads)
                source_map[source.name] = count
                total_count += count

                total_row[source.name] += count  # accumulate per-source total

            total_row['total_count'] += total_count  # accumulate grand total

            employee_sales_data.append({
                'employee_name': user.name,
                **source_map,
                'total_count': total_count
            })

        # Add total row at end of list
        employee_sales_data.append(total_row)

        return employee_sales_data, all_sources

    def get_employee_lead_quality_data(self, from_date=None, to_date=None):
        users = request.env['res.users'].search([
            ('employee_id.department_id.name', '=', 'Sales')
        ])

        lead_qualities = [
            ('new', '🆕  New'),
            ('waiting_for_admission', '⏳  Waiting for Admission'),
            ('admission', '🎓  Admission'),
            ('hot', '🔥  Hot'),
            ('warm', '🌞  Warm'),
            ('cold', '❄️  Cold'),
            ('bad_lead', '⚠️  Bad Lead'),
            ('crash_lead', '💥  Crash Lead'),
            ('not_responding', '🚫  Not Responding'),
        ]
        quality_keys = [q[0] for q in lead_qualities]
        quality_labels = [q[1] for q in lead_qualities]

        employee_quality_data = []

        total_row = {key: 0 for key in quality_keys}
        total_row['employee_name'] = 'Total'
        total_row['total_count'] = 0

        if from_date:
            from_date = fields.Date.from_string(from_date)
        if to_date:
            to_date = fields.Date.from_string(to_date)

        for user in users:
            quality_map = {quality: 0 for quality in quality_keys}
            total_count = 0

            for quality in quality_keys:
                domain = [
                    ('lead_owner', '=', user.employee_id.id),
                    ('state', '=', 'qualified'),
                    ('lead_quality', '=', quality),
                ]
                if from_date and to_date:
                    domain += [
                        ('date_of_adding', '>=', from_date),
                        ('date_of_adding', '<=', to_date)
                    ]

                leads = request.env['leads.logic'].search(domain)
                count = len(leads)
                quality_map[quality] = count
                total_count += count

                total_row[quality] += count

            total_row['total_count'] += total_count

            employee_quality_data.append({
                'employee_name': user.name,
                **quality_map,
                'total_count': total_count
            })

        employee_quality_data.append(total_row)

        return employee_quality_data, quality_labels, quality_keys

    def get_employee_sales_data(self, from_date=None, to_date=None):
        users = request.env['res.users'].search([
            ('employee_id.department_id.name', '=', 'Sales')
        ])
        employee_sales_data = []

        if from_date:
            from_date = fields.Date.from_string(from_date)
        if to_date:
            to_date = fields.Date.from_string(to_date)

        for user in users:
            domain = [
                ('lead_owner', '=', user.employee_id.id),
                ('state', 'in', ['qualified'])
            ]
            if from_date and to_date:
                domain += [('admission_date', '>=', from_date), ('admission_date', '<=', to_date)]

            sales_orders = request.env['leads.logic'].search(domain)

            total_sale_amount = sum(order.batch_fee for order in sales_orders if order.batch_fee)
            number_of_sales = len(sales_orders)

            employee_sales_data.append({
                'name': user.name,
                'total_sale_amount': total_sale_amount,
                'number_of_sales': number_of_sales,
            })
        print(employee_sales_data, 'emp sale date')
        return employee_sales_data

    # def get_top_product(self, sales_orders):
    #     product_sales = {}
    #     for order in sales_orders:
    #         product = order.course_id.name
    #         if product not in product_sales:
    #             product_sales[product] = 0
    #         product_sales[product] += 1
        # if product_sales:
        #     return max(product_sales, key=product_sales.get)
        # return _('N/A')

    def get_sales_revenue(self, period='today'):
        domain = self.get_sales_revenue_domain(period=period)
        orders = request.env['leads.logic'].search(domain)
        # Sum up the total amounts
        total_revenue = int(sum(order.batch_fee for order in orders))
        return helper_tools.format_to_indian_currency(total_revenue)
        # return round(total_revenue,3)

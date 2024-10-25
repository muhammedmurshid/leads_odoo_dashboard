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
        employee_sales_data = self.get_employee_sales_data()
        product_sales_data = self.get_product_sales_data()  # Corrected this line
        zero_sales_employees = self.get_employees_with_zero_sales()  # Fetch employees with zero sales

        print(zero_sales_employees, 'data')
        return {
            'sales_today': self.get_sales_revenue(period='today'),
            'sales_this_week': self.get_sales_revenue(period='week'),
            'sales_this_month': self.get_sales_revenue(period='month'),
            'sales_this_quarter': self.get_sales_revenue(period='quarter'),
            'sales_this_year': self.get_sales_revenue(period='year'),
            'employee_sales_data': employee_sales_data,
            'product_sales_data': product_sales_data,
            'zero_sales_employees': zero_sales_employees

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

    def get_employees_with_zero_sales(self):
        users = request.env['res.users'].search([('employee_id.department_id.name', '=', 'Sales')])  # Get all users
        zero_sales_employees = []

        for user in users:
            # Check if the user has any sales orders
            sales_orders = request.env['sale.order'].search(
                [('user_id', '=', user.id), ('state', 'in', ['sale', 'done'])])
            if not sales_orders:
                print('not sale order')# If no sales orders found
                zero_sales_employees.append({'id': user.id, 'name': user.name})  # Add ID

        return zero_sales_employees

    def get_product_sales_data(self):
        # This function should query product sales and return them in the required format
        products = request.env['product.product'].search([])

        product_sales_data = []
        for product in products:
            # Get the sale order lines related to the product
            sale_order_lines = request.env['sale.order.line'].search([('product_id', '=', product.id)])

            # Calculate total sales and number of sales
            total_sales = sum(sale_order_lines.mapped('order_id.amount_total'))  # Total amount from related sale orders
            number_of_sales = len(sale_order_lines.mapped('order_id'))  # Count unique sale orders

            product_sales_data.append({
                'name': product.name,
                'total_sale_amount': total_sales,
                'number_of_sales': number_of_sales
            })
        return product_sales_data

    def get_employee_sales_data(self):
        # Search for all users where their employee's department is "Sales"
        users = request.env['res.users'].search([
            ('employee_id.department_id.name', '=', 'Sales')
        ])

        employee_sales_data = []

        for user in users:
            print(user.id, 'emp')  # For debugging
            # Search for sales orders related to the user in 'sale' or 'done' states
            sales_orders = request.env['sale.order'].search([
                ('user_id', '=', user.id),
                ('state', 'in', ['sale', 'done'])
            ])

            # Calculate total sales amount for this user
            total_sales_amount = sum(order.amount_total for order in sales_orders)

            # Fetch the top product sold by this user
            top_product = self.get_top_product(sales_orders)

            # Append the data for this user
            employee_sales_data.append({
                'name': user.name,
                'total_sale_amount': total_sales_amount,
                'number_of_sales': len(sales_orders),
                'top_product': top_product
            })

        return employee_sales_data

    def get_top_product(self, sales_orders):
        product_sales = {}
        for order in sales_orders:
            for line in order.order_line:
                product = line.product_id.name
                if product not in product_sales:
                    product_sales[product] = 0
                product_sales[product] += line.product_uom_qty
        if product_sales:
            return max(product_sales, key=product_sales.get)
        return _('N/A')

    def get_sales_revenue(self, period='today'):
        domain = self.get_sales_revenue_domain(period=period)
        orders = request.env['sale.order'].search(domain)
        # Sum up the total amounts
        total_revenue = int(sum(order.amount_total for order in orders))
        return helper_tools.format_to_indian_currency(total_revenue)
        # return round(total_revenue,3)

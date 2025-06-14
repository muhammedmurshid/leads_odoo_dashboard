{
    'name': "Leads Custom Dashboards",
    'author': 'Murshid',
    'version': "17.0.0.0",
    'sequence': "0",
    'depends': ['base','web', 'custom_leads'],
    'data': [
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'leads_odoo_dashboard/static/src/xml/dashboard_template.xml',
            'leads_odoo_dashboard/static/src/css/style.scss',
            'leads_odoo_dashboard/static/src/js/dashboards.js',
        ],
    },
    'demo': [],
    'summary': "Leads Custom Dashboards",
    'description': "Leads Custom Dashboards",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': False
}
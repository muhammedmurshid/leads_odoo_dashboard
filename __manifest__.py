{
    'name': "Tiju's Custom Dashboards",
    'author': 'Rizwaan',
    'version': "17.0.0.0",
    'sequence': "0",
    'depends': ['base','web', 'sale','crm'],
    'data': [
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'tijus_odoo_dashboards/static/src/xml/dashboard_template.xml',
            'tijus_odoo_dashboards/static/src/css/style.scss',
            'tijus_odoo_dashboards/static/src/js/dashboards.js',
        ],
    },
    'demo': [],
    'summary': "Tiju's Custom Dashboards",
    'description': "Tiju's Custom Dashboards",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': False
}
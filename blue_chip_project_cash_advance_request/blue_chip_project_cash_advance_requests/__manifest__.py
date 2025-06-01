# -*- coding: utf-8 -*-
{
    'name': "BC Cash Advance Form",

    'summary': """
        Module for managing cash advance requests for each project milestone""",

    'description': """
        Module for managing cash advance requests for each project milestone
    """,

    'author': "Lotus Beta Analytics",
    'website': "https://www.lotusbetaanalytics.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','sale','hr','account'],
    

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/current_request_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'web_icon': 'blue_chip_project_cash_advance_requests/static/description/blue_chip_dummy_icon_128.png',
    
    'installable': True,
    'application': True,
}

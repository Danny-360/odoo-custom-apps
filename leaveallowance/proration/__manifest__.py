# -*- coding: utf-8 -*-
{
    'name': "Proration Template",

    'summary': """
        IDL Proration for Leave allowance""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Lotus Beta Analytics",
    'website': "https://www.lotusbetaanalytics.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services/Allowance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['leaveallowance'],
    'application': False,
    # always loaded
    'data': [
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
{
    'name': "Leave Allowance",

    'summary': """
        IDL Leave allowance""",

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
    'depends': ['base','mail'],
    'application': True,
    # always loaded
    'data': [
        "security/allowance_security.xml",
        "security/ir.model.access.csv",
        "views/mail_template.xml",
        "views/allowance_view.xml",
        "views/menu.xml"
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}

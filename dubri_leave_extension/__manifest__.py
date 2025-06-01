# -*- coding: utf-8 -*-
{
    'name': "dubri_leave_extension",

    'summary': """
        Module is designed to allow the MD notification on leave approval for Dubril oil""",

    'description': """
        Module is designed to allow the MD notification on leave approval for Dubril oil
    """,

    'author': "Ifeoluwa",
    'website': "https://www.lotusbetaanalytics.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_holidays','mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/email_templates.xml',
        'security/user_access.xml',
        'views/hr_leave_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

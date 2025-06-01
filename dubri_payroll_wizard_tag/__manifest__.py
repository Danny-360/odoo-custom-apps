# -*- coding: utf-8 -*-
{
    'name': "Employee Payroll Tag",

    'summary': """
        This module allows employees to be selected by their tags""",

    'description': """
        This module allows employees to be selected by their tags
    """,

    'author': "Daniel",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
         'views/hr_payslip_employees_view.xml',
    ],

    'installable': True,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

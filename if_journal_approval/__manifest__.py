# -*- coding: utf-8 -*-
{
    'name': "if_journal_approval",

    'summary': """
        Manage approval on Vendor Bills, Journals and Purchase Receipts""",

    'description': """
        Manage approval on Vendor Bills, Journals and Purchase Receipts. Access group has been created for the approval
        Manager
    """,

    'author': "Ifeoluwa",
    'website': "https://www.tunnox.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/user_groups.xml',
        'wizard/journal_rejection_reason.xml',
        'views/account_move_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

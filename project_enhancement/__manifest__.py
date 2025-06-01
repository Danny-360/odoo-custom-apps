
{
    'name': "Project Enhancement",

    'summary': """
        This module populates departmental team's details""",

    'description': """
        This module adds the fields for both Departmental Manager and Team lead
    """,

    'author': "LBA ERP TEAM",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services/Project Enhancement',
    # 'category': 'Services/Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project','hr','hr_expense','planning','approvals','account'],

    # always loaded
    'data': [
        'security/project_groups.xml',
        'security/project_rules.xml',
        'security/ir.model.access.csv',
        'data/role_assignment_wizard_action.xml',
        'views/views.xml',
        'views/role_assignment_wizard_view.xml',
        'views/project_templates.xml',
        # 'views/views_menu.xml',
        # 'security/project_action_defaults.xml',
        # 'views/templates.xml',
        
    ],

    'installable': True,
    'application': False,
    'auto_install': False,

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

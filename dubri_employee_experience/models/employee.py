from odoo import models, fields, api

class pfa(models.Model):
    """docstring for pension fund admin"""
    _name = "employee.pfa"
    _description = "Pension Fund Administrators"

    name = fields.Char(string="Name", required=True)



class Employeeprofile(models.Model):
    _inherit = "hr.employee"

    next_of_kin = fields.Char("Next of Kin", groups="hr.group_hr_user", tracking=True)
    next_of_kin_phone = fields.Char("Next of Kin Phone", groups="hr.group_hr_user")
    next_of_kin_address = fields.Char("Next of Kin Address", groups="hr.group_hr_user")
    pfa = fields.Many2one(comodel_name="employee.pfa", string="Pension Fund Admin", groups="hr.group_hr_user")
    pfa_pin = fields.Char(string="Pension PIN", groups="hr.group_hr_user", copy=False)
    payee_id = fields.Char(string="Payee ID", groups="hr.group_hr_user", copy=False)
    religion = fields.Selection([('christianity', 'Christianity'),
                                 ('islam', 'Islam'),
                                 ('others', 'Others'),], string="Religion", groups="hr.group_hr_user")
    relationship = fields.Selection([
        ('husband', 'Husband'),
        ('wife', 'Wife'),
        ('son', 'Son'),
        ('daughter', 'Daughter'),
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
    ], string="Relationship", groups="hr.group_hr_user")


    _sql_constraints =[('pin_uniq', 'unique (pfa_pin)', "Pension Pin already exist on another employee."), ('payee_uniq', 'unique (payee_id)', "Payee ID already exist on another employee.") ]

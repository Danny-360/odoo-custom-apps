from odoo import models, fields, api

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    employee_tag_ids = fields.Many2many(
        'hr.employee.category',
        string='Employee Tags'
    )

    @api.onchange('employee_tag_ids', 'employee_ids')
    def _onchange_employee_filters(self):
        if self.employee_tag_ids:
            # Get employees who have ALL the selected tags
            employees = self.env['hr.employee'].search([
                ('category_ids', 'in', self.employee_tag_ids.ids)
            ])
            employees = employees.filtered(
                lambda emp: set(self.employee_tag_ids.ids).issubset(set(emp.category_ids.ids))
            )
            if self.employee_ids:
                # If employee_ids already selected, intersect both filters
                employees = employees.filtered(lambda e: e.id in self.employee_ids.ids)
            self.employee_ids = [(6, 0, employees.ids)]
        elif self.employee_ids:
            # Only filter by selected employee_ids if no tags
            self.employee_ids = [(6, 0, self.employee_ids.ids)]
        else:
            self.employee_ids = [(5, 0, 0)]  # Clear field if no filters

    def compute_sheet(self):
        """ Override to apply tag filtering at runtime """
        if self.employee_tag_ids and not self.employee_ids:
            employees = self.env['hr.employee'].search([
                ('category_ids', 'in', self.employee_tag_ids.ids),
                ('contract_id.state', '=', 'open')
            ])
            employees = employees.filtered(
                lambda emp: set(self.employee_tag_ids.ids).issubset(set(emp.category_ids.ids))
            )
            self.employee_ids = [(6, 0, employees.ids)]
        return super(HrPayslipEmployees, self).compute_sheet()
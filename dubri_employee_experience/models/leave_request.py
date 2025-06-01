from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.constrains('date_from', 'date_to', 'employee_id')
    def _check_department_leaves(self):
        for leave in self:
            if leave.state == 'draft':
                continue

            overlapping_leaves = self.env['hr.leave'].search([
                ('state', 'in', ['confirm', 'validate1', 'validate']),
                ('employee_id.department_id', '=', leave.employee_id.department_id.id),
                ('date_from', '<=', leave.date_to),
                ('date_to', '>=', leave.date_from),
                ('id', '!=', leave.id),
            ])

            if overlapping_leaves:
                raise ValidationError(_("Another employee from your department/team is already on leave for the selected dates."))
